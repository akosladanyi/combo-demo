from django.conf.urls import patterns, url, include
from main import views

urlpatterns = patterns('main.views',
   url(r'^getnetwork/$',
       views.GetNetworkView.as_view(),
       name='main:get_network'),
)
