from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.awards_list, name='list'),
]
