from django.urls import reverse_lazy
from django.shortcuts import HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum

from .models import Tracking, Bills, Railcars


# Create your views here.


class TrackerView(LoginRequiredMixin, generic.ListView):
    template_name = 'tracker/tracking.html'
    queryset = Tracking.objects.all().order_by('-time')
    context_object_name = 'tracking_list'


class TrackDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tracking
    context_object_name = 'track'
    template_name_suffix = '_detail'


class TrackCreateView(LoginRequiredMixin, generic.CreateView):
    model = Tracking
    fields = ['railcar', 'amount', 'comment']
    success_url = reverse_lazy('tracker:tracking')
    template_name_suffix = '_new'


class MainLoginView(LoginView):
    redirect_authenticated_user = True
    redirect_field_name = 'tracker:index'


class BillsListView(LoginRequiredMixin, generic.ListView):  # Вью для вывода списка платежей
    template_name = 'tracker/bills.html'
    # Суммируем количество топлива по вагонам в поле total
    queryset = Bills.objects.all().annotate(total=Sum('railcars__volume')).order_by('-bill_date', '-bill')
    context_object_name = 'bills'
    model = Bills


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'tracker/index.html'


class BillsCreateView(LoginRequiredMixin, generic.CreateView):
    model = Bills
    template_name = 'tracker/bills_new.html'
    fields = ['bill', 'amount', 'supplier', 'bill_date', 'supply_date']
    success_url = reverse_lazy('tracker:bills')
