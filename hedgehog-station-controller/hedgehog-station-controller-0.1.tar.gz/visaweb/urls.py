from django.conf.urls import url

from . import views

app_name = 'visaweb'
urlpatterns = [
    # ex: /visaweb/
    url(r'^$', views.IndexView.as_view(), name='index'),
    # ex: /visaweb/agilent_hp_8920b/
    url(r'^(?P<slug>[-\w]+)/$', views.DetailView.as_view(), name='detail'),
    # ex: /visaweb/agilent_hp_8920b/results/1/
    url(r'^/results/(?P<pk>[0-9]+)/$', views.ResultsView.as_view(), name='results'),

    # # ex: /visaweb/
    # url(r'^$', views.index, name='index'),
    # # ex: /visaweb/agilent_hp_8920b/
    # url(r'^(?P<device_alias>\w+)/$', views.detail, name='detail'),
    # # ex: /visaweb/agilent_hp_8920b/results/1/
    # url(r'^(?P<device_alias>\w+)/results/(?P<event_id>[0-9]+)/$', views.results, name='results'),

    # ex: /visaweb/agilent_hp_8920b/spectrum/
    url(r'^(?P<device_alias>\w+)/spectrum/$', views.spectrum, name='spectrum'),
    # ex: /visaweb/agilent_hp_8920b/waterfall/
    url(r'^(?P<device_alias>\w+)/waterfall/$', views.waterfall, name='waterfall'),

    url(r'^(?P<device_alias>\w+)/read/$', views.read, name='read'),
    url(r'^(?P<device_alias>\w+)/write/$', views.write, name='write'),
    url(r'^(?P<device_alias>\w+)/query/$', views.query, name='query'),

]