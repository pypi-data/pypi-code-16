# -*- coding: utf-8 -*-

from django.db import models

from model_utils.models import TimeStampedModel


class OutboxRequestLog(TimeStampedModel):
    request_uuid = models.UUIDField(db_index=True)
    request_path = models.TextField()
    request_body = models.TextField(null=True, blank=True)
    request_flagged_duplicate = models.BooleanField()
    response_status_code = models.IntegerField()
