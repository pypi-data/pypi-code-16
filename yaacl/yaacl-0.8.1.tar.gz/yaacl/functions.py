# -*- coding:utf-8 -*-
from django.db.models.query_utils import Q
from yaacl.models import ACL

__author__ = 'Daniel Alkemic Czuba <dc@danielczuba.pl>'


def get_acl_resources(user):
    """
    :type user: django.contrib.auth.models.User
    :type name : str

    Checks if user has rights to given resource
    """
    return ACL.objects.filter(
        Q(user=user) | Q(group__in=user.groups.all())
    ).distinct().values_list('resource', flat=True)


def has_access(user, resource_name, resources=None):
    """
    :type user: django.contrib.auth.models.User
    :type name : str
    :type resources : list

    Checks if user has rights to given resource
    """
    if not user or not user.is_authenticated():
        return False

    if user.is_superuser:
        return True

    if resources is None:
        resources = get_acl_resources(user)

    return any(map(lambda r: r.startswith(resource_name), resources))


def has_all_access(user, name, resources=None):
    """
    :type user: django.contrib.auth.models.User
    :type name : str
    :type resources : list

    Checks if user has rights to given resource
    """
    if not user or not user.is_authenticated():
        return False

    if user.is_superuser:
        return True

    if resources is None:
        resources = get_acl_resources(user)

    user_resources = set(filter(lambda r: r.startswith(name), resources))
    available_resources = set(filter(
        lambda r: r.startswith(name), ACL.acl_list.keys(),
    ))
    return user_resources == available_resources
