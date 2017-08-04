from django.conf.urls import url

from . import views

app_name = 'tracker'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^details/(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^new/', views.TrackCreateView.as_view(), name='new'),
]
