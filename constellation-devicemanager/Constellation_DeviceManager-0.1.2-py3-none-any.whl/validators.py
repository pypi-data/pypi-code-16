import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from netaddr.strategy import eui48

# Regex that matches valid hostnames
hostname = "^(?=.{1,255}$)[0-9A-Za-z](?:(?:[0-9A-Za-z]|-){0,61}[0-9A-Za-z])?(?:\.[0-9A-Za-z](?:(?:[0-9A-Za-z]|-){0,61}[0-9A-Za-z])?)*\.?$" # noqa 401


def validate_mac(value):
    if not eui48.valid_str(value):
        raise ValidationError(
            _('%(value) is not a properly formatted MAC address'),
            params={'value': value},
        )


def validate_hostname(value):
    if not re.match(hostname, value):
        raise ValidationError(
            ('%(value) is not a valid hostname'),
            params={'value': value},
        )
