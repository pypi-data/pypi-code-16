import json
import re

import jinja2
import jinja2.ext
from django.conf import settings
from django.contrib.messages.context_processors import get_messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.html import format_html, mark_safe
from wagtail.wagtailcore.models import Page


def debug_variable(variable):
    """Print all the fields available on a variable"""
    return format_html('<pre>{}</pre>', dir(variable))


@jinja2.contextfunction
def csrf_field(context):
    """Print the hidden CSRF token field"""
    csrf_token = context.get('csrf_token')
    if not csrf_token or csrf_token == 'NOTPROVIDED':
        return format_html("")

    return format_html("<input{}>", flatatt({
        'type': 'hidden',
        'name': 'csrfmiddlewaretoken',
        'value': csrf_token}))


def url(name, *args, **kwargs):
    """Reverse a URL name. Alias of ``django.core.urlresolvers.reverse``"""
    return reverse(name, args=args or None, kwargs=kwargs or None)


@jinja2.contextfunction
def site_root(context):
    """Get the root page for the site"""
    # This lookup will be cached on the intermediary objects, so this will only
    # hit the DB once per request
    return context['request'].site.root_page.specific


def svg_inline(name):
    """
    Inline an SVG image. SVG images are expected to be a template, not kept in
    the static files
    """
    return mark_safe(render_to_string('svgs/%s.svg' % name))


@jinja2.contextfunction
def breadcrumbs(context, page=None):
    """Print the top navigation menu for this site"""
    request = context.get('request')
    root = site_root(context)
    if page is None:
        page = context.get('page')
    ancestors = page.get_ancestors().filter(depth__gte=root.depth)

    return jinja2.Markup(render_to_string('tags/breadcrumbs.html', {
        'page': page,
        'ancestors': ancestors,
        'request': request,
    }))


def js_context(key, value):
    """ Adds variables to the window for use by other scripts. """
    return format_html('window.appData["{0}"] = {1};'.format(key.upper(), json.dumps(value)))


def model_classname(model_or_instance):
    """
    Generate a CSS class name from a Page model

    Usage::

        <html class="{{ self|model_classname }}">
    """
    if isinstance(model_or_instance, Page):
        model_or_instance = model_or_instance.content_type.model_class()

    try:
        meta = model_or_instance._meta
        return 'page-{0}-{1}'.format(meta.app_label, meta.model_name)
    except AttributeError:
        return ''


@jinja2.contextfunction
def messages(context):
    """Get any messages from django.contrib.messages framework"""
    return get_messages(context.get('request'))


def json_dumps(value):
    """
    Dump the value to a JSON string. Useful when sending values to JavaScript
    """
    return jinja2.Markup(json.dumps(value, cls=DjangoJSONEncoder))


not_digit_re = re.compile(r'[^0-9+]+')


def tel(value):
    return 'tel:{}'.format(not_digit_re.sub('-', value).strip('-'))


class Extension(jinja2.ext.Extension):
    def __init__(self, environment):
        super(Extension, self).__init__(environment)

        self.environment.globals.update({
            'breadcrumbs': breadcrumbs,
            'site_root': site_root,
            'csrf_field': csrf_field,
            'static': staticfiles_storage.url,
            'url': url,
            'svg': svg_inline,
            'js_context': js_context,
            'model_classname': model_classname,
            'messages': messages,
            'DEBUG': settings.DEBUG,
        })

        self.environment.filters.update({
            'model_classname': model_classname,
            'debug_variable': debug_variable,
            'json': json_dumps,
            'tel': tel,
        })
