"""
    ml_markdown template tags and filters
"""
import re
from django import template
from django.utils.text import mark_safe
from django.template.defaultfilters import stringfilter
from django.apps import apps
import misaka
import bleach
from ml_markdown.utils.default_renderer import DefaultRenderer

register = template.Library()
parse = misaka.Markdown(
    DefaultRenderer(),
    apps.get_app_config('ml_markdown').misaka_extensions
)

TAGS_WHITE_LIST = apps.get_app_config('ml_markdown').tags
ATTRIBUTES_WHITE_LIST = apps.get_app_config('ml_markdown').attributes

entity_replace = {
    '\xa0': '&nbsp;',
    '↩': '&#8617;'
}


@register.filter(is_safe=False)
@stringfilter
def to_html(value):
    """
        Render convert Markdown code to html in template.
        This filter do not clean the html output.

        :param value: The markdown code
        :return: The unclean html output.
    """
    return parse(value)


@register.filter(is_safe=True)
@stringfilter
def clean(value, white_list=None):
    """
        Clean html code

        :param value: html code to clean
        :param white_list: tags and attributes white list. Must be a dict lie this :
            {
                'tags': ['h1', 'h2', ...]
                'attributes': {
                    'h1': ['id'],
                    ...
                }
            }
            if not provided, use the whitelist in the configuration class.
            if provides only one of the two keys, the other will use the list in the configuration class

        :return: clean html code
    """
    tags = TAGS_WHITE_LIST
    attributes = ATTRIBUTES_WHITE_LIST

    if isinstance(white_list, dict):
        if 'tags' in white_list:
            tags = white_list['tags']
        if 'attributes' in white_list:
            attributes = white_list['attributes']

    output = bleach.clean(
        text=value,
        tags=tags,
        attributes=attributes
    )

    for k, v in entity_replace.items():
        output = re.sub(k, v, output)

    return mark_safe(output)


@register.filter(is_safe=True)
@stringfilter
def to_cleaned_html(value, white_list=None):
    """
        Shortcut to |to_html|clean

        :param value: Text to parse and clean
        :param white_list: Same as clean filter

        :return: Clean html code
    """
    return mark_safe(clean(to_html(value), white_list))


@register.filter(is_safe=True)
@stringfilter
def sectionize(value, end_mark='<div class="footnotes">'):
    output = []
    section_open = False

    lines = value.splitlines()
    lines_number = len(lines)
    i = 1

    for line in lines:
        if re.match(r'^<h1', line):
            if section_open:
                output.append('</section>')
                output.append('<section>')
            else:
                output.append('<section>')
                section_open = True

        if end_mark in line:
            output.append('</section>')
            i = False

        output.append(line)

        if i and i == lines_number:
            output.append('</section>')
        if i:
            i += 1

    return mark_safe('\n'.join(output))
