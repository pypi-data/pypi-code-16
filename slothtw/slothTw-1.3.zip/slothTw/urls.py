# -*- coding: utf-8 -*-
from django.conf.urls import url
from slothTw import views

urlpatterns = [
  url(r'^get/clist$', views.clist, name='clist'),
  url(r'^get/cvalue$', views.cvalue, name='cvalue'),
  url(r'^get/comment$', views.Comment.as_view(), name='Comment'),
  url(r'^put/reply$', views.Comment.as_view(), name='reply'),
]