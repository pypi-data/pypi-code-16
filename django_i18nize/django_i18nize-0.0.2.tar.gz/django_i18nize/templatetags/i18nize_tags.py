from django import template
register = template.Library()

from django_i18nize.utils import get_translation

@register.simple_tag
def i18n_switch(key, language=None, values=None):
    return get_translation(key, language, values)