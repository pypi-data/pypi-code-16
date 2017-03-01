# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(
        regex="^MailchimpFormContent/~create/$",
        view=views.MailchimpFormContentCreateView.as_view(),
        name='MailchimpFormContent_create',
    ),
    url(
        regex="^MailchimpFormContent/(?P<pk>\d+)/~delete/$",
        view=views.MailchimpFormContentDeleteView.as_view(),
        name='MailchimpFormContent_delete',
    ),
    url(
        regex="^MailchimpFormContent/(?P<pk>\d+)/$",
        view=views.MailchimpFormContentDetailView.as_view(),
        name='MailchimpFormContent_detail',
    ),
    url(
        regex="^MailchimpFormContent/(?P<pk>\d+)/~update/$",
        view=views.MailchimpFormContentUpdateView.as_view(),
        name='MailchimpFormContent_update',
    ),
    url(
        regex="^MailchimpFormContent/$",
        view=views.MailchimpFormContentListView.as_view(),
        name='MailchimpFormContent_list',
    ),
	]
