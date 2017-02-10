# coding: utf-8

from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

if "notify" in settings.INSTALLED_APPS:
    from notify.signals import notify as notification
else:
    notification = None


def notify_awarded(badge):
    if not notification:
        return

    verb = _("awarded a badge")
    nf_type = "badge_awarded"

    notification.send(
        badge.user,
        recipient=badge.user,
        actor=badge.user,
        verb=verb,
        target=badge,
        nf_type=nf_type,
        target_url=reverse('awards:list')
    )
