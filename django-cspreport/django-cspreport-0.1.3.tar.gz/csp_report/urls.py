# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import csp_report_view

urlpatterns = [
    url(r'^$', csp_report_view, name='csp_report_view'),
]
