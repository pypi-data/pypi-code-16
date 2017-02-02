# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(
        regex="^OutboxRequestLog/~create/$",
        view=views.OutboxRequestLogCreateView.as_view(),
        name='OutboxRequestLog_create',
    ),
    url(
        regex="^OutboxRequestLog/(?P<pk>\d+)/~delete/$",
        view=views.OutboxRequestLogDeleteView.as_view(),
        name='OutboxRequestLog_delete',
    ),
    url(
        regex="^OutboxRequestLog/(?P<pk>\d+)/$",
        view=views.OutboxRequestLogDetailView.as_view(),
        name='OutboxRequestLog_detail',
    ),
    url(
        regex="^OutboxRequestLog/(?P<pk>\d+)/~update/$",
        view=views.OutboxRequestLogUpdateView.as_view(),
        name='OutboxRequestLog_update',
    ),
    url(
        regex="^OutboxRequestLog/$",
        view=views.OutboxRequestLogListView.as_view(),
        name='OutboxRequestLog_list',
    ),
	]
