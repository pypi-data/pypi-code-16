from django import template

register = template.Library()

@register.filter
def singleline(value):
	if value:
		return value.strip().replace('\n', ' ')
	return value
