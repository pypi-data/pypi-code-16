from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CBRConfig(AppConfig):
    name = 'cbr'
    verbose_name = _('CBR currency rates')
