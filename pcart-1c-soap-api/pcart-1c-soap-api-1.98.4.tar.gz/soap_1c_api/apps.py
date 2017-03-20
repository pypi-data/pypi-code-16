from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PCartImport1CConfig(AppConfig):
    name = 'soap_1c_api'
    verbose_name = _('Integration with 1C (SOAP)')
