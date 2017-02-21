# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

from django import template
from django.contrib.staticfiles.finders import find as find_staticfile
from django.contrib.staticfiles.storage import staticfiles_storage

from path2css import generate_css_names_from_string, Output, LinkOutput

register = template.Library()

@register.simple_tag(takes_context=False)
def path2css(path, prefix='', suffix='', midpoint='-', split_on='/'):
    variations = generate_css_names_from_string(item=path, prefix=prefix, suffix=suffix,
                                           midpoint=midpoint, split_on=split_on)
    return Output(variations)



@register.simple_tag(takes_context=False)
def css4path(path, prefix='', suffix='', midpoint='-', directory='css', split_on='/'):
    variations = generate_css_names_from_string(item=path, prefix=prefix, suffix=suffix,
                                           midpoint=midpoint, split_on=split_on)
    found_files = []
    for variation in variations:
        filename = os.path.join(directory, '{}.css'.format(variation))
        found = find_staticfile(path=filename)
        if found is not None:
            # import pdb; pdb.set_trace()
            found_file = staticfiles_storage.url(filename)
            found_files.append(found_file)
    return LinkOutput(found_files)
