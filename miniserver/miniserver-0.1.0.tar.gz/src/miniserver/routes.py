import warnings
from collections import OrderedDict

from functools import singledispatch

import functools

ROUTES = OrderedDict()
DEFAULT_PAGE_NAMES = {'index': ''}


def route(url=None, **kwargs):
    """
    Decorator that defines a route in your web page.
    """

    if callable(url) and url.__name__ in DEFAULT_PAGE_NAMES:
        return route(DEFAULT_PAGE_NAMES[url.__name__], **kwargs)(url)
    elif callable(url):
        return route(url.__name__, **kwargs)(url)

    def decorator(func):
        url_route = func.__name__ if url is None else url.lstrip('/')
        if url_route in ROUTES:
            warnings.warn('duplicate route: %r' % url)
        else:
            ROUTES[url_route] = wrapped_view(func, **kwargs)
        return func
    return decorator


def regex_escape(st):
    return st


def regex_from_route(route):
    """
    Convert a route string in the form part1/part2/{varname}/ to a Django url
    regex.
    """
    regex, tail = '', route

    while tail:
        pre, sep, tail = tail.partition('{')
        regex += regex_escape(pre)
        if sep:
            varname, sep, tail = tail.partition('}')
            if not sep:
                raise ValueError('brakets in route string do not match: %r' % route)
            regex += r'(?P<%s>[^\/]*)' % varname

    return regex


def make_url_patterns():
    """
    Return a list of url_patterns from the registered routes.
    """

    from django.conf.urls import url

    # Index is handled differently.
    routes = dict(ROUTES)
    routes.pop('', None)

    result = []
    for route, view in routes.items():
        result.append(url(regex_from_route(route), view))
    return result


def update_context(context):
    import miniserver

    context.setdefault('settings', miniserver.settings)


def render(request, template, context=None, **kwargs):
    from django.shortcuts import render

    context = dict(context or {}, **kwargs)
    update_context(context)
    return render(request, template, context)


@singledispatch
def wrap_to_request(data, request, template='base.html'):
    return render(request, template, {'body': data})


@wrap_to_request.register(dict)
def _(data, request, template='base.html'):
    return render(request, template, data)


def wrapped_view(view, **kwargs):
    """
    Wraps a miniserver view function in a Django-compatible view function.
    """

    @functools.wraps(view)
    def django_view(request, **dj_kwargs):
        kwargs['request'] = request
        return wrap_to_request(view(**dj_kwargs), **kwargs)

    return django_view