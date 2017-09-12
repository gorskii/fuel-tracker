from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'tracker'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^railcars/$', views.TrackerView.as_view(), name='railcars'),
    url(r'^railcars/new/$', views.TrackCreateView.as_view(), name='track_new'),
    url(r'^bills/$', views.BillsListView.as_view(), name='bills'),
    url(r'^bills/new/$', views.bill_create, name='bills_new'),
    url(r'^tracking/$', views.MonitoringView.as_view(), name='tracking'),
    url(r'^tracking/details/(?P<pk>[0-9]+)/$', views.TrackDetailView.as_view(), name='track_detail'),
    url(r'^login/$', views.MainLoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
]

