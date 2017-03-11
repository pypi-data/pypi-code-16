from __future__ import absolute_import, unicode_literals
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django_i18nize import settings as plugin_settings


class i18nizeConfig(AppConfig):
    name = 'django_i18nize'
    verbose_name = _("Django i18nize")

    def ready(self):
        plugin_settings.patch_all()