# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import warnings

from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

try:
    from collections import UserList
except ImportError:
    from UserList import UserList
from django.utils.six import python_2_unicode_compatible

__version_info__ = '0.2.1'
__version__ = '0.2.1'
version = '0.2.1'
VERSION = '0.2.1'
__all__ = ['get_version', 'generate_css_names_from_string',
           'request_path_to_css_names']

def get_version():
    return version  # pragma: no cover


def generate_css_names_from_string(item, split_on, prefix='', suffix='', midpoint=''):
    newpath = tuple(part for part in item.strip(split_on).split(split_on)
                    if part)
    # If the thing is empty, just return an empty tuple
    if not newpath:
        return ()
    newpath_length = len(newpath) + 1
    variations = (newpath[0:l] for l in range(1, newpath_length))
    # If there's a prefix and it doesn't end with a sensible separator (given
    # the valid names of CSS identifiers), add midpoint.
    if prefix and not prefix.endswith(('-', '_')):
        prefix = '%s%s' % (prefix, midpoint)
    # same as prefix, but start, rather than end
    if suffix and not suffix.startswith(('-', '_')):
        suffix = '%s%s' % (midpoint, suffix,)
    finalised_variations = (
        '%s%s%s' % (prefix, midpoint.join(variation), suffix)
        for variation in variations
    )
    return finalised_variations


def request_path_to_css_names(item, prefix='', suffix='', midpoint=''):
    # TODO: remove this function.
    warnings.warn(
        "request_path_to_css_names() is scheduled to be removed, and should be "
        "replaced with generate_css_names_from_string() with a valid "
        "split_on argument",
        PendingDeprecationWarning
    )
    return generate_css_names_from_string(item=item, split_on='/',
                                          prefix=prefix, suffix=suffix,
                                          midpoint=midpoint)


@python_2_unicode_compatible
class Output(UserList):
    string_template = "{}"
    string_separator = " "

    def __str__(self):
        """
        Used when doing something like:
        {% path2css ... as OUTVAR %}
        {{ OUTVAR }}
        """
        parts = (self.string_template.format(force_text(x)) for x in self.data)
        return mark_safe(self.string_separator.join(parts))

    def __html__(self):
        """
        Used in {% path2css x y %} is used directly
        """
        return force_text(self)

    def __getitem__(self, item):
        """
        Used when doing something like:
        {% path2css ... as OUTVAR %}
        {% for x in OUTVAR %}{{ x }}{% endfor %}
        """
        return mark_safe(super(Output, self).__getitem__(item))


class LinkOutput(Output):
    string_template = '<link href="{}" rel="stylesheet" type="text/css" />'
    string_separator = "\n"

def context_processor(request):
    return {
        "PATH2CSS": Output(request_path_to_css_names(request.path, midpoint='-')),
    }
