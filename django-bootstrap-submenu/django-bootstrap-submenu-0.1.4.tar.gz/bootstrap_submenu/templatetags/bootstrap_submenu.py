from django import template
from django.utils.safestring import mark_safe
from .. import get_js,get_css

register = template.Library()


@register.simple_tag
def bootstrap_submenu_js():
    return mark_safe('<script type="text/javascript" src="%s"></script>'%get_js())


@register.simple_tag
def bootstrap_submenu_css():
    return mark_safe('<link rel="stylesheet" href="%s" type="text/css">'%get_css())
