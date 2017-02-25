from django import template

register = template.Library()

@register.filter
def mul(value, arg):
	"""Multiplies the arg and the value."""
	if type(value) is str or type(value) is unicode:
		value = int(value)
	return value * arg

@register.filter
def sub(value, arg):
	"""Subtracts the arg from the value."""
	if type(value) is str or type(value) is unicode:
		value = int(value)
	return value - arg

@register.filter
def div(value, arg):
	"""Divides the value by the arg."""
	if type(value) is str or type(value) is unicode:
		value = int(value)
	if arg:
		return value / arg
	else:
		return 0

@register.filter
def mod(value, arg):
	"""Modulo the value by the arg."""
	if type(value) is str or type(value) is unicode:
		value = int(value)
	return value % arg
