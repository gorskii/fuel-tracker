from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'tracker'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^details/(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^new/', views.TrackCreateView.as_view(), name='new'),
    url(r'^login/$', views.TrackingLoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
]
