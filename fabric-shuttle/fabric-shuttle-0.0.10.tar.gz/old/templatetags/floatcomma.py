from django.contrib.humanize.templatetags.humanize import intcomma
from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter(is_safe=True)
def floatcomma(value, arg=-1):
	"""Combines the intcomma and floatformat filters into one."""
	i = intcomma(value)
	f = floatformat(value, arg)
	index = i.find('.')
	if index != -1:
		i = i[:index]
	index = f.find('.')
	if index != -1:
		f = f[index+1:].rstrip('0')
		if f:
			return '%s.%s' % (i, f)
	return i
