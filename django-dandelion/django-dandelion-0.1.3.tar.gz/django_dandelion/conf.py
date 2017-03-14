# -*- coding: utf-8

from __future__ import unicode_literals

from django.conf import settings

DANDELION_HOST = getattr(settings, 'DANDELION_HOST', 'api.dandelion.eu')
DANDELION_TOKEN = getattr(settings, 'DANDELION_TOKEN', None)
DANDELION_USE_CACHE = getattr(settings, 'DANDELION_USE_CACHE', True)
