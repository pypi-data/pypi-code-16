from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from netaddr.strategy import eui48

def validate_mac(value):
    if not eui48.valid_str(value):
        raise ValidationError(
            _('%(value) is not a properly formatted MAC address'),
            params={'value': value},
        )
