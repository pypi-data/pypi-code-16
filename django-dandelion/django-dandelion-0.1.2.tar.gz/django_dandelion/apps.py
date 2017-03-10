# -*- coding: utf-8

from __future__ import unicode_literals

from django.apps import AppConfig

from .conf import DANDELION_HOST, DANDELION_TOKEN
from .exceptions import DandelionSettingsException


class DandelionConfig(AppConfig):
    name = 'django_dandelion'
    label = 'django_dandelion'
    verbose_name = 'Django Dandelion'

    def ready(self):
        if not DANDELION_HOST:
            raise DandelionSettingsException('You must set DANDELION_HOST in settings.py.')
        if not DANDELION_TOKEN:
            raise DandelionSettingsException('You must set DANDELION_TOKEN in settings.py.')
