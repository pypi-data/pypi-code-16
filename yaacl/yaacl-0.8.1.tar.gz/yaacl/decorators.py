# -*- coding:utf-8 -*-
from functools import wraps

from django.utils.decorators import method_decorator, available_attrs
from yaacl.functions import has_access

from .views import no_access
from .models import ACL
from .signals import register_resource


def acl_register_view(name=None, resource=None):
    """
    :type name: unicode
    :type resource: str
    """

    def decorator(view_func, name, resource):
        if resource is None:
            resource = "%s.%s" % (
                view_func.__module__,
                view_func.__name__,
            )

        signal_returned = register_resource.send(
            sender='acl_register_view',
            resource=resource,
            name=name,
        )

        if signal_returned:
            signal_returned = signal_returned[-1]
            resource = signal_returned[1].get('resource', None)
            name = signal_returned[1].get('name', None)

        if resource not in ACL.acl_list:
            ACL.acl_list[resource] = name

        @wraps(view_func, assigned=available_attrs(view_func))
        def wrapped_view(request, *args, **kwargs):
            """
            :type request: django.http.request.HttpRequest
            """
            has_access_to_resource = (
                request.user.is_authenticated() and
                has_access(request.user, resource)
            )
            if has_access_to_resource:
                return view_func(request, *args, **kwargs)
            else:
                return no_access(request)

        return wrapped_view

    return lambda view_func: decorator(view_func, name, resource)


def acl_register_class(name=None, resource=None):
    def klass_decorator(klass, name, resource):
        if resource is None:
            resource = "%s.%s" % (klass.__module__, klass.__name__)

        klass.dispatch = method_decorator(
            acl_register_view(name, resource)
        )(klass.dispatch)

        return klass

    return lambda klass: klass_decorator(klass, name, resource)
