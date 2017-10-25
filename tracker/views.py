from django.urls import reverse_lazy
from django.shortcuts import HttpResponseRedirect, render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum
from django.forms import inlineformset_factory, modelformset_factory
from django.utils import timezone

from .forms import RailcarsModelForm, RailcarAddForm, BillsModelForm, TrackingModelForm, MainLoginForm
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


@login_required
@permission_required('tracker.add_tracking')
def railcar_release(request, pk):
    """ Устанавливает статус "отпущен" для вагона и время отпуска для трека """
    if request.method == 'GET':
        track = get_object_or_404(Tracking, pk=pk)
        railcar = track.railcar
        railcar.is_released = True
        railcar.save(update_fields=('is_released',))
        track.release_time = timezone.now()
        track.save(update_fields=('release_time',))
    return HttpResponseRedirect(reverse_lazy('tracker:railcars'))


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


# class TrackCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
#     permission_required = 'tracker.add_tracking'
#     form_class = TrackingModelForm
#     success_url = reverse_lazy('tracker:railcars')
#     template_name = 'tracker/tracking_new.html'
#     context_object_name = 'form'
#
#     def get_context_data(self, **kwargs):
#         context = super(TrackCreateView, self).get_context_data(**kwargs)
#         railcar_form = RailcarsModelForm()
#         context['railcar'] = railcar_form
#         return context
#
#     def form_valid(self, form):
#         r = RailcarsModelForm(self.request.POST)
#         # r.instance.railcar = self.request.POST['railcar']
#         # r.instance.fuel = self.request.POST['fuel']
#         # r.instance.volume = self.request.POST['volume']
#         # Делаем отметку пользователя, принявшего вагон
#         form.instance.accepted_by = self.request.user
#         # Делаем пометку, что вагон принят
#         r.instance.is_accepted = True
#         r.instance.save()
#         return super(TrackCreateView, self).form_valid(form)


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
        context['railcars_available'] = get_railcars_available()
        # FIXME Возвращаются два идентичных элемента контекста, bills и object_list. Поправить, если возможоно
        return context


class BillsDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    """ This class based view replaced by bill_detail view below """

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
        context['railcars_form'] = RailcarAddForm()

        return context


@login_required
@permission_required('tracker.add_bills')
def bill_detail(request, pk):
    context = {}
    bill = get_object_or_404(Bills, pk=pk)
    railcars = bill.railcars_set.all().order_by('railcar')
    context['bill'] = bill
    context['railcars_list'] = railcars
    # context['fuel_total'] = railcars.aggregate(Sum('volume')).get('volume__sum', 0.00)
    context['fuel_diff'] = get_fuel_diff(railcars)
    context['date_diff'] = get_date_diff(railcars)
    context['railcars_stat'] = get_railcars_stat()
    context['railcars_available'] = get_railcars_available(bill)
    if request.method == 'POST':
        railcar = get_object_or_404(Railcars, pk=request.POST['railcar'])
        if railcar.bill is None:
            railcar.bill = bill
            railcar.save(update_fields=['bill'])
        return HttpResponseRedirect(reverse_lazy('tracker:bills_detail', kwargs={'pk': pk}))
    else:
        context['railcars_form'] = RailcarAddForm()
    return render(request, template_name='tracker/bills_detail.html', context=context)


@login_required
@permission_required('tracker.add_bills')
def railcar_free(request, pk):
    """ Отвязывает вагон от сделки """
    railcar = get_object_or_404(Railcars, pk=pk)
    bill_pk = railcar.bill_id
    if request.method == 'GET':
        railcar.bill = None
        railcar.save(update_fields=['bill'])
    return HttpResponseRedirect(reverse_lazy('tracker:bills_detail', kwargs={'pk': bill_pk}))


@login_required
@permission_required('tracker.add_bills')
def bill_create(request):
    # railcar_formset = inlineformset_factory(Bills, Railcars,
    #                                         form=RailcarsModelForm,
    #                                         extra=0,
    #                                         min_num=1,
    #                                         validate_min=True,
    #                                         can_delete=False)
    if request.method == 'POST':
        bill_form = BillsModelForm(request.POST)
        if bill_form.is_valid():
            bill_form.save()
            return HttpResponseRedirect(reverse_lazy('tracker:bills'))
            #     created_bill = bill_form.save(commit=False)
            #     formset = railcar_formset(request.POST, instance=created_bill)
            #     if formset.is_valid():
            #         created_bill.save()
            #         formset.save()
            #         return HttpResponseRedirect(reverse_lazy('tracker:bills'))
            # else:
            #     formset = railcar_formset(request.POST)
    else:
        bill_form = BillsModelForm()
        # bill = Bills()
        # formset = railcar_formset(instance=bill)
    # return render(request, 'tracker/bills_new.html',
    #               {'bill_form': bill_form,
    #                'railcars_formset': formset})
    return render(request, 'tracker/bills_new.html', {'bill_form': bill_form})


class BillUpdateView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'tracker.add_bills'
    model = Bills
    form_class = BillsModelForm
    context_object_name = 'bill'
    template_name_suffix = '_edit'

    def get_success_url(self):
        return reverse_lazy('tracker:bills_detail', kwargs={'pk': self.object.id})


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
        context['railcars_list'] = Railcars.objects.filter(is_accepted=False).order_by('bill__payment_date')
        context['railcars_stat'] = get_railcars_stat()
        return context


class MainLoginView(LoginView):
    redirect_authenticated_user = True
    redirect_field_name = 'tracker:index'
    authentication_form = MainLoginForm


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'tracker/index.html'


@login_required
@permission_required('tracker.add_tracking')
def track_create(request):
    if request.method == 'POST':
        railcar_form = RailcarsModelForm(request.POST)
        if railcar_form.is_valid():
            created_railcar = railcar_form.save(commit=False)
            tracking_form = TrackingModelForm(request.POST)
            if tracking_form.is_valid():
                created_railcar.is_accepted = True
                created_railcar.save()
                tracking_form.instance.railcar = created_railcar
                tracking_form.instance.accepted_by = request.user
                tracking_form.save()
                return HttpResponseRedirect(reverse_lazy('tracker:railcars'))
        else:
            tracking_form = TrackingModelForm(request.POST)
    else:
        railcar_form = RailcarsModelForm()
        tracking_form = TrackingModelForm()
    return render(request, 'tracker/tracking_new.html',
                  {'railcar': railcar_form,
                   'track': tracking_form})


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
    :return: Словарь разниц между датой оплаты и временем приёма
    :rtype: dict
    """
    diff = {}

    for railcar in railcars:
        if Tracking.objects.filter(railcar=railcar).exists():
            track = Tracking.objects.get(railcar=railcar)
            if railcar.bill:
                if railcar.bill.payment_date is None:
                    # если оплата ещё не прошла, берём за дату оплаты крайнюю допустимую
                    d = railcar.bill.bill_date + timezone.timedelta(days=5)
                else:
                    d = railcar.bill.payment_date
                # За точку отсчёта принимаем 15:00 даты отгрузки
                dt = timezone.make_aware(timezone.datetime(d.year, d.month, d.day)) + timezone.timedelta(hours=15)
                td = dt - track.time  # type: timezone.timedelta
                diff[railcar] = td
                # else:
                #     diff[railcar] = None  # None если нет привязки к счёту
    return diff


def get_bill_stat():
    """
    Получить статус сделки
    :return: Словарь Сделка : Статус
    :rtype: dict

    Статус:
    0 - успешно принят
    1 - неделя с даты оплаты, есть непринятые вагоны
    2 - различие в количестве топлива
    3 - в процессе приёма
    4 - просрочка даты оплаты
    5 - последний день оплаты
    """
    bills_stat = {}
    railcars = Railcars.objects.all()
    fuel_diff = get_fuel_diff(railcars)  # type: dict
    date_diff = get_date_diff(railcars)  # type: dict

    for railcar in date_diff:  # Все вагоны в этом словаре приняты
        bills_stat[railcar.bill] = 0

    for railcar in date_diff:
        # for item in railcars.filter(bill=railcar.bill):
        #     if item not in date_diff:
        #         bills_stat[railcar.bill] = 3
        if abs(fuel_diff[railcar]) >= 100:  # Погрешность в кг
            bills_stat[railcar.bill] = 2
            # elif date_diff[railcar] < timezone.timedelta(0):
            #     bills_stat[railcar.bill] = 1

    today = timezone.now().date()

    bills = Bills.objects.all()
    for bill in bills:
        if bill.payment_date:
            limit = bill.payment_date + timezone.timedelta(days=7)
            if get_railcars_available(bill) > 0 and today >= limit:
                bills_stat[bill] = 1

        else:
            limit = bill.bill_date + timezone.timedelta(days=5)
            if today == limit:
                bills_stat[bill] = 5
            elif today > limit:
                bills_stat[bill] = 4

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
        if abs(fuel_diff[railcar]) >= 100:  # Погрешность в кг
            tracks_stat[railcar] = 2
        # if not railcar.is_released and timezone.now() - railcar.tracking_set.:
        #     tracks_stat[railcar] = 1

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
        if railcar.bill.payment_date is None:
            d = railcar.bill.bill_date + timezone.timedelta(days=5)
        else:
            d = railcar.bill.payment_date
        # За конец дня принимаем 18:00 даты отгрузки
        end = timezone.make_aware(timezone.datetime(d.year, d.month, d.day)) + timezone.timedelta(hours=18)
        if now >= end:
            railcars_stat[railcar] = 1  # просрочен
        elif d == today:
            railcars_stat[railcar] = 2  # прием сегодня
        else:
            railcars_stat[railcar] = 0  # время ещё не пришло
    return railcars_stat


def get_railcars_count(bill):
    if bill.volume > 0:
        count = bill.volume // 61 + 1
    else:
        count = 0
    return count


def get_railcars_available(bill=None):
    if bill:
        railcars_assigned_count = bill.railcars_set.count()
        return get_railcars_count(bill) - railcars_assigned_count
    else:
        railcars_available = {}
        bills = Bills.objects.all()
        if bills:
            for item in bills:
                railcars_available[item] = get_railcars_count(item) - item.railcars_set.count()
        return railcars_available
