from django.conf import settings
from importlib import import_module
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Default configuration
DEFAULT_CONFIG = {
    "project_id": None,
    "live": False,
    'destination_dir': os.path.realpath(os.path.join(BASE_DIR, 'staticfiles', 'locale'))
}

# Update CONFIG with user added configuration
CONFIG = DEFAULT_CONFIG.copy()
if hasattr(settings, 'DJANGO_I18NIZE_CONFIG'):
    for key, value in settings.DJANGO_I18NIZE_CONFIG.iteritems():
        CONFIG[key] = value
else:
    raise AttributeError('django_i18nize requires DJANGO_I18NIZE_CONFIG inside of you project settings file. Please read the README.md on github for more details.')

# Add DJANGO_I18NIZE_CONFIG to root settings
def patch_settings():
    setattr(settings, 'DJANGO_I18NIZE_CONFIG', CONFIG)


def patch_all():
    patch_settings()