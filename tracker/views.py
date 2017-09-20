from django.urls import reverse_lazy
from django.shortcuts import HttpResponseRedirect, render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum
from django.forms import inlineformset_factory
from django.utils import timezone

from .forms import RailcarsModelForm, BillsModelForm, TrackingModelForm, MainLoginForm
from .models import Tracking, Bills, Railcars


class TrackerView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'tracker.add_tracking'
    template_name = 'tracker/tracking.html'
    # queryset = Tracking.objects.all().order_by('-time')
    context_object_name = 'tracking_list'

    def get_queryset(self):
        # Выводим список треков только для текущего пользователя
        queryset = Tracking.objects.filter(accepted_by=self.request.user)
        return queryset.order_by('-time')  # Новые вверху списка


class TrackDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    permission_required = 'tracker.view_tracking'
    model = Tracking
    context_object_name = 'track'
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        context = super(TrackDetailView, self).get_context_data(**kwargs)
        railcar = Railcars.objects.all()
        context['fuel_diff'] = get_fuel_diff(railcar)
        context['date_diff'] = get_date_diff(railcar)
        return context


class TrackCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    permission_required = 'tracker.add_tracking'
    form_class = TrackingModelForm
    success_url = reverse_lazy('tracker:railcars')
    template_name = 'tracker/tracking_new.html'

    def form_valid(self, form):
        # Делаем отметку пользователя, принявшего вагон
        form.instance.accepted_by = self.request.user
        # Делаем пометку, что вагон принят
        curr_railcar = form.instance.railcar.id
        r = Railcars.objects.get(pk=curr_railcar)
        r.is_accepted = True
        r.save()
        return super(TrackCreateView, self).form_valid(form)


class BillsListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):  # Вью для вывода списка платежей
    permission_required = 'tracker.view_bills'
    template_name = 'tracker/bills.html'
    # Суммируем количество топлива по вагонам в поле total
    queryset = Bills.objects.all().annotate(total=Sum('railcars__volume')).order_by('-bill_date', '-bill')
    context_object_name = 'bills'

    def get_context_data(self, **kwargs):
        context = super(BillsListView, self).get_context_data(**kwargs)
        context['bills_stat'] = get_bill_stat()
        context['railcars_stat'] = get_railcars_stat()
        # FIXME Возвращаются два идентичных элемента контекста, bills и object_list. Поправить, если возможоно
        return context


class BillsDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    permission_required = 'tracker.view_bills'
    model = Bills
    context_object_name = 'bill'
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        context = super(BillsDetailView, self).get_context_data(**kwargs)
        railcars = self.object.railcars_set.all().order_by('railcar')
        context['railcars_list'] = railcars
        context['fuel_total'] = railcars.aggregate(Sum('volume')).get('volume__sum', 0.00)
        context['fuel_diff'] = get_fuel_diff(railcars)
        context['date_diff'] = get_date_diff(railcars)
        context['railcars_stat'] = get_railcars_stat()
        return context


class MonitoringView(TrackerView):
    permission_required = 'tracker.view_tracking'
    template_name = 'tracker/monitoring.html'

    def get_queryset(self):
        # Выводим список треков для всех пользователей
        queryset = Tracking.objects.all()
        return queryset.order_by('-time')  # Новые вверху списка

    def get_context_data(self, **kwargs):
        context = super(MonitoringView, self).get_context_data(**kwargs)
        context['tracks_stat'] = get_tracks_stat()
        context['railcars_list'] = Railcars.objects.filter(is_accepted=False).order_by('bill__supply_date')
        context['railcars_stat'] = get_railcars_stat()
        return context


class MainLoginView(LoginView):
    redirect_authenticated_user = True
    redirect_field_name = 'tracker:index'
    authentication_form = MainLoginForm


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'tracker/index.html'


@login_required
@permission_required('tracker.add_bills')
def bill_create(request):
    railcar_formset = inlineformset_factory(Bills, Railcars,
                                            form=RailcarsModelForm,
                                            extra=0,
                                            min_num=1,
                                            validate_min=True,
                                            can_delete=False)
    if request.method == 'POST':
        bill_form = BillsModelForm(request.POST)
        if bill_form.is_valid():
            created_bill = bill_form.save(commit=False)
            formset = railcar_formset(request.POST, instance=created_bill)
            if formset.is_valid():
                created_bill.save()
                formset.save()
                return HttpResponseRedirect(reverse_lazy('tracker:bills'))
        else:
            formset = railcar_formset(request.POST)
    else:
        bill_form = BillsModelForm()
        bill = Bills()
        formset = railcar_formset(instance=bill)
    return render(request, 'tracker/bills_new.html',
                  {'bill_form': bill_form,
                   'railcars_formset': formset})


def get_fuel_diff(railcars):
    """
    Получить разницы в количестве топлива
    :return: Словарь разниц между количеством топлива в платеже и фактически принятым
    :rtype: dict
    """
    diff = {}

    for railcar in railcars:
        if Tracking.objects.filter(railcar=railcar).exists():
            track = Tracking.objects.get(railcar=railcar)
            diff[railcar] = railcar.volume - track.amount
    return diff


def get_date_diff(railcars):
    """
    Получить разницы в датах
    :return: Словарь разниц между датой поставки и временем приёма
    :rtype: dict
    """
    diff = {}

    for railcar in railcars:
        if Tracking.objects.filter(railcar=railcar).exists():
            track = Tracking.objects.get(railcar=railcar)
            d = railcar.bill.supply_date
            # За точку отсчёта принимаем 15:00 даты отгрузки
            dt = timezone.make_aware(timezone.datetime(d.year, d.month, d.day)) + timezone.timedelta(hours=15)
            td = dt - track.time  # type: timezone.timedelta
            diff[railcar] = td
    return diff


def get_bill_stat():
    """
    Получить статусы платежей
    :return: Словарь Платёж : Статус
    :rtype: dict

    Статус:
    0 - успешно принят
    1 - просрочка даты поставки
    2 - различие в количестве топлива
    3 - в процессе приёма
    """
    bills_stat = {}
    railcars = Railcars.objects.all()
    fuel_diff = get_fuel_diff(railcars)  # type: dict
    date_diff = get_date_diff(railcars)  # type: dict

    for railcar in date_diff:  # Все вагоны в этом словаре приняты
        bills_stat[railcar.bill] = 0

    for railcar in date_diff:
        for item in railcars.filter(bill=railcar.bill):
            if item not in date_diff:
                bills_stat[railcar.bill] = 3
        if fuel_diff[railcar] != 0:
            bills_stat[railcar.bill] = 2
        elif date_diff[railcar] < timezone.timedelta(0):
            bills_stat[railcar.bill] = 1

    return bills_stat


def get_tracks_stat():
    """
    Получить статусы треков
    :return: Словарь Трек : Статус
    :rtype: dict

    Статус:
    0 - успешно принят
    1 - просрочка даты поставки
    2 - различие в количестве топлива
    """
    tracks_stat = {}
    railcars = Railcars.objects.all()
    fuel_diff = get_fuel_diff(railcars)  # type: dict
    date_diff = get_date_diff(railcars)  # type: dict

    for railcar in date_diff:  # Все вагоны в этом словаре приняты
        tracks_stat[railcar] = 0

    for railcar in date_diff:
        if fuel_diff[railcar] != 0:
            tracks_stat[railcar] = 2
        elif date_diff[railcar] < timezone.timedelta(0):
            tracks_stat[railcar] = 1

    return tracks_stat


def get_railcars_stat():
    """
    Получить статусы непринятых вагонов
    :return: Словарь Вагон : Статус
    :rtype: dict

    Статус:
    0 - день поставки ещё не настал
    1 - просрочка даты поставки
    2 - поставка сегодня
    """
    railcars_stat = {}
    railcars = Railcars.objects.filter(is_accepted=False)
    today = timezone.localdate()
    now = timezone.now()

    for railcar in railcars:
        d = railcar.bill.supply_date
        # За конец дня принимаем 18:00 даты отгрузки
        end = timezone.make_aware(timezone.datetime(d.year, d.month, d.day)) + timezone.timedelta(hours=18)
        if now >= end:
            railcars_stat[railcar] = 1  # просрочен
        elif d == today:
            railcars_stat[railcar] = 2  # прием сегодня
        else:
            railcars_stat[railcar] = 0  # время ещё не пришло
    return railcars_stat
