from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import autodiscover_modules


class AwardsConfig(AppConfig):
    name = 'awards'
    verbose_name = _("Awards")

    def ready(self):
        autodiscover_modules('badges')
        autodiscover_modules('badges_receivers')
