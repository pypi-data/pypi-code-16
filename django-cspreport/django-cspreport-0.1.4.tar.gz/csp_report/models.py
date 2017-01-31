# -*- coding: utf-8 -*-
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.template.defaultfilters import truncatechars


class CSPReport(models.Model):
    host = models.TextField(blank=True, null=True, default='')
    document_uri = models.TextField()
    blocked_uri = models.TextField()
    referrer = models.TextField(blank=True, null=True, default='')

    body = JSONField(default={}, blank=True, null=True)
    request_meta = JSONField(default={}, blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)

    @property
    def short_blocked_uri(self):
        return truncatechars(self.blocked_uri, 100)