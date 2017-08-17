from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView

from .models import Tracking


# Create your views here.


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'tracker/index.html'
    queryset = Tracking.objects.all().order_by('-time')
    context_object_name = 'tracking_list'

# def index(request):  # Показываем список треков
#     tracking_list = Tracking.objects.all().order_by('-time')
#     context = {
#         'tracking_list': tracking_list,
#     }
#     return render(request, 'tracker/index.html', context)
#
#


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Tracking
    template_name = 'tracker/detail.html'
    context_object_name = 'track'

# def detail(request, track_id):  # Показываем строку из списка
#     track = get_object_or_404(Tracking, id=track_id)
#     context = {
#         'track': track,
#     }
#     return render(request, 'tracker/detail.html', context)


class TrackCreateView(LoginRequiredMixin, generic.CreateView):
    model = Tracking
    fields = ['railcar', 'amount', 'comment']
    success_url = reverse_lazy('tracker:index')
    template_name_suffix = '_new'


class TrackingLoginView(LoginView):
    redirect_authenticated_user = True
    redirect_field_name = 'tracker:index'
