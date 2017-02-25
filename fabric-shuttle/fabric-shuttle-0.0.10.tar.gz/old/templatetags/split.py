from django import template

register = template.Library()

@register.filter
def split(value, arg):
	if value:
		return [s for s in value.split(str(arg)) if s]
	return value
