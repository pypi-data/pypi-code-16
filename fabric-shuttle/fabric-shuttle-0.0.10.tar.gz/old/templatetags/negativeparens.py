from django import template

register = template.Library()

@register.filter(is_safe=True)
def negativeparens(value):
	"""Surrounds the value with parentheses if it starts with a -."""
	value = str(value)
	if value[0] == '-':
		return '(%s)' % value[1:]
	return value
