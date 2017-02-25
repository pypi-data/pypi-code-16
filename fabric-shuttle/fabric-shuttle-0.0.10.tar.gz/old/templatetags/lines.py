from django import template

register = template.Library()

@register.filter
def lines(value):
	if value:
		return [s for s in value.split('\n') if s]
	return value
