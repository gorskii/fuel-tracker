from django.urls import reverse_lazy
from django.shortcuts import HttpResponseRedirect, render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.forms import inlineformset_factory

from .forms import RailcarsModelForm, BillsModelForm, TrackingModelForm, MainLoginForm
from .models import Tracking, Bills, Railcars


class TrackerView(LoginRequiredMixin, generic.ListView):
    template_name = 'tracker/tracking.html'
    # queryset = Tracking.objects.all().order_by('-time')
    context_object_name = 'tracking_list'

    def get_queryset(self):
        # Выводим список треков только для текущего пользователя
        queryset = Tracking.objects.filter(accepted_by=self.request.user)
        return queryset.order_by('-time')  # Новые вверху списка


class TrackDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tracking
    context_object_name = 'track'
    template_name_suffix = '_detail'


class TrackCreateView(LoginRequiredMixin, generic.CreateView):
    model = Tracking
    form_class = TrackingModelForm
    success_url = reverse_lazy('tracker:tracking')
    template_name_suffix = '_new'

    def form_valid(self, bill_form):
        # Делаем отметку пользователя, принявшего вагон
        bill_form.instance.accepted_by = self.request.user
        return super(TrackCreateView, self).form_valid(bill_form)


class MainLoginView(LoginView):
    redirect_authenticated_user = True
    redirect_field_name = 'tracker:index'
    authentication_form = MainLoginForm


class BillsListView(LoginRequiredMixin, generic.ListView):  # Вью для вывода списка платежей
    template_name = 'tracker/bills.html'
    # Суммируем количество топлива по вагонам в поле total
    queryset = Bills.objects.all().annotate(total=Sum('railcars__volume')).order_by('-bill_date', '-bill')
    context_object_name = 'bills'
    model = Bills


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'tracker/index.html'


@login_required
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
                   'railcars_formset': formset}
                  )
