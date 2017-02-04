# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from .managers import ACLManager

from django.conf import settings

user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
group_model = getattr(settings, 'ACL_GROUP_USER_MODEL', 'auth.Group')


@python_2_unicode_compatible
class ACL(models.Model):
    acl_list = {}

    resource = models.CharField(
        _("Resource name"),
        max_length=255,
        db_index=True,
    )
    display = models.CharField(
        _("displayed name"),
        max_length=255,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        _("Creation time"),
        auto_now_add=True,
    )
    is_available = models.BooleanField(
        _("Is available to assign"),
        default=True,
    )

    user = models.ManyToManyField(
        user_model,
        verbose_name=_('User'),
        blank=True,
        related_name='acl',
    )
    group = models.ManyToManyField(
        group_model,
        verbose_name=_('User'),
        blank=True,
        related_name='acl',
    )

    objects = ACLManager()

    class Meta:
        app_label = 'yaacl'

    def __str__(self):
        if self.display:
            return "%s (%s)" % (self.display, self.resource)
        else:
            return self.resource
