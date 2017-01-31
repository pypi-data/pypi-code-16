# -*- coding: utf-8 -*-
from django.contrib.postgres.fields import JSONField
from django.db import models


class CSPReport(models.Model):
    host = models.TextField(blank=True, null=True, default='')
    document_uri = models.TextField()
    blocked_uri = models.TextField()
    referrer = models.TextField(blank=True, null=True, default='')

    body = JSONField(default={}, blank=True, null=True)
    request_meta = JSONField(default={}, blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)
