from django import template
from django.template.defaultfilters import stringfilter
from django.template.defaultfilters import urlize
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def urlizeblank(value, autoescape=None):
	"""Urlize the string and set the url targets to _blank."""
	return mark_safe(urlize(value, autoescape).replace('<a', '<a target="_blank"'))
