from django import template
from django.conf import settings

register = template.Library()

@register.filter
def absoluteurl(path, domain=None):
	"""Builds an absolute url with either the provided domain (typically taken from get_current_site) or the first domain found in settings.ALLOWED_HOSTS."""
	if path and type(path) != unicode:
		path = unicode(path)
	if path and not path.startswith('http://'):
		if domain:
			if path.startswith('/'):
				return 'http://%s%s' % (domain, path)
			else:
				return 'http://%s/%s' % (domain, path)
		elif len(settings.ALLOWED_HOSTS):
			domain = settings.ALLOWED_HOSTS[0]
			if domain.startswith('.'):
				domain = domain[1:]
			if path.startswith('/'):
				return 'http://%s%s' % (domain, path)
			else:
				return 'http://%s/%s' % (domain, path)
	return path
