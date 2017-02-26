# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.sites.models import Site
from djangofloor.models import Notification
from inventicode import views


from django.contrib.admin import site
site.unregister(Notification)
site.unregister(Site)

urlpatterns = [
    url(r'^print_labels\.html$', views.print_labels, name='print_labels'),
    url(r'^update_category\.html$', views.update_category, name='update_category'),
    url(r'^update_state\.html$', views.update_state, name='update_state'),
    url(r'^batch_update\.html$', views.batch_update, name='batch_update'),
]
