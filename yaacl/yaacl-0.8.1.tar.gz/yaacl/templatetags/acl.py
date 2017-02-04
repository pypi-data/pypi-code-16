# -*- coding:utf-8 -*-
from django import template
from yaacl import functions

register = template.Library()


@register.filter
def has_access(user, resource):
    """
    :type user: django.contrib.auth.models.User
    :type name : str

    Checks if user has rights to given resource
    """
    return functions.has_access(user, resource)


@register.filter
def has_all_access(user, resource):
    """
    :type user: django.contrib.auth.models.User
    :type name : str

    Checks if user has rights to given resource
    """
    return functions.has_all_access(user, resource)
