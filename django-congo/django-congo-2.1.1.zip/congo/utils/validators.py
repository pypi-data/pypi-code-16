# -*- coding: utf-8 -*-
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

POLISH_PHONE_REGEX = RegexValidator(regex = r'^(\+48|0048)?\d{9}$', message = _(u"Obowiązujący format numeru telefonu to \"999999999\". Dozwolone jest 9 cyfr"))
PHONE_REGEX = RegexValidator(regex = r'^\+?1?\d{9,15}$', message = _(u"Obowiązujący format numeru telefonu to \"+99999999999. Dozwolone od 9 do 15 cyfr."))
