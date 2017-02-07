from __future__ import absolute_import, unicode_literals

import collections

from django.core.exceptions import PermissionDenied

from acls.models import AccessControlList
from permissions import Permission

from . import MAYAN_VERSION


if MAYAN_VERSION[0:2] <= (2, 1):
    def filter_by_access(permission, user, queryset):
        try:
            Permission.check_permissions(
                requester=user, permissions=(permission,)
            )
        except PermissionDenied:
            return AccessControlList.objects.filter_by_access(
                permission=permission, user=user, queryset=queryset
            )
        else:
            return queryset

    def check_access(permissions, user, obj, related=None):
        if not isinstance(permissions, collections.Iterable):
            permissions = (permissions,)

        try:
            return Permission.check_permissions(
                requester=user, permissions=permissions
            )
        except PermissionDenied:
            return AccessControlList.objects.check_permissions(
                requester=user, permissions=permissions
            )
else:
    def filter_by_access(permission, user, queryset):
        return AccessControlList.objects.filter_by_access(
            permission=permission, user=user, queryset=queryset
        )

    def check_access(*args, **kwargs):
        return AccessControlList.objects.check_access(*args, **kwargs)
