from django.apps import AppConfig

from django.utils.translation import ugettext_lazy as _


class AwardsConfig(AppConfig):
    name = 'awards'
    verbose_name = _("Awards")

    def ready(self):
        pass
