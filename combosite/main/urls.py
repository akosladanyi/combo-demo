from django.conf.urls import patterns, url, include
from main import views

urlpatterns = patterns('main.views',
    url(r'^$',
        views.HomeView.as_view(),
        name='home'),
    url(r'^getnetwork/$',
        views.GetNetworkView.as_view(),
        name='main:get_network'),
    url(r'^setspeed/$',
        views.SetSpeedView.as_view(),
        name='main:set_speed'),
    url(r'^getconnectedclients/$',
        views.GetConnectedClientsView.as_view(),
        name='main:get_connected_clients'),
)
