from django.db import models

from common.models import DateTimeModelMixin


class TestDateTimeModel(DateTimeModelMixin, models.Model):
    title = models.CharField(max_length=30)
