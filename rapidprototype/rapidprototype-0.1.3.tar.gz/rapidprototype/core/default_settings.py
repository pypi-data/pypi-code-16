import os
from django.conf import settings

SITE_PAGES_DIRECTORY = hasattr(settings, 'SITE_PAGES_DIRECTORY') and settings.SITE_PAGES_DIRECTORY or 'pages'
