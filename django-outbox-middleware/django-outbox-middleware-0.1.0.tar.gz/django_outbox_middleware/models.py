# -*- coding: utf-8 -*-

from django.db import models

from model_utils.models import TimeStampedModel


class OutboxRequestLog(TimeStampedModel):
    request_uuid = models.UUIDField()
    request_path = models.TextField()
    request_body = models.TextField(null=True, blank=True)
    response_status_code = models.IntegerField()
