# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	MailchimpFormContent,
)


class MailchimpFormContentCreateView(CreateView):

    model = MailchimpFormContent


class MailchimpFormContentDeleteView(DeleteView):

    model = MailchimpFormContent


class MailchimpFormContentDetailView(DetailView):

    model = MailchimpFormContent


class MailchimpFormContentUpdateView(UpdateView):

    model = MailchimpFormContent


class MailchimpFormContentListView(ListView):

    model = MailchimpFormContent

