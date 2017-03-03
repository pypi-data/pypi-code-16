from __future__ import absolute_import
from django.conf import settings


class DjangoSettings(object):
    def get(self, key):
        return getattr(settings, key)
