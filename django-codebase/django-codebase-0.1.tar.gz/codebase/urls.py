from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^a_create_api/$', views.a_create_api),
    url(r'^a_get_apis/$', views.a_get_apis),
]


