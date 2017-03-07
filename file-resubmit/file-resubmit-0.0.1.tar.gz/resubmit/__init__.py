from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


if 'resubmit' not in settings.CACHES:
    raise ImproperlyConfigured(
        "CACHES['resubmit'] is not defined in settings.py")
