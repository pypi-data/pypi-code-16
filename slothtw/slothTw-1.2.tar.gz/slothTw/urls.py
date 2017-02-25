# -*- coding: utf-8 -*-
from django.conf.urls import url
from slothTw import views

urlpatterns = [
  url(r'^get/clist$', views.clist, name='clist'),
  url(r'^get/cvalue$', views.cvalue, name='cvalue'),
  url(r'^get/cComment$', views.cComment, name='cComment'),
  url(r'^put/reply$', views.reply, name='reply'),
]