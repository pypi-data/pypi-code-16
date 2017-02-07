from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from navigation import Menu

from .compat import MAYAN_VERSION


if MAYAN_VERSION[0:2] <= (2, 1):
    menu_cabinets = Menu(name='cabinets menu')
else:
    menu_cabinets = Menu(
        icon='fa fa-columns', label=_('Cabinets'), name='cabinets menu'
    )
