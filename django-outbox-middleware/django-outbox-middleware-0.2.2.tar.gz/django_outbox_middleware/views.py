# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	OutboxRequestLog,
)


class OutboxRequestLogCreateView(CreateView):

    model = OutboxRequestLog


class OutboxRequestLogDeleteView(DeleteView):

    model = OutboxRequestLog


class OutboxRequestLogDetailView(DetailView):

    model = OutboxRequestLog


class OutboxRequestLogUpdateView(UpdateView):

    model = OutboxRequestLog


class OutboxRequestLogListView(ListView):

    model = OutboxRequestLog

