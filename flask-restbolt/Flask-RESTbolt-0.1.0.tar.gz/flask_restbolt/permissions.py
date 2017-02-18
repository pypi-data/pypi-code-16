#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'costular'


class BasePermission(object):
    """
    A base class from which all permission classes should inherit.
    Thanks to Django REST Framework (https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/permissions.py)
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True


class AllowAny(BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(self, request, view):
        return True


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        pass
        # TODO