from django.conf.urls import url
from django.views.static import serve

def static_serve_url(static_url, static_root, name=None, view=serve):
	static_url = static_url.strip('/')
	if static_url:
		static_url = '^%s/(?P<path>.*)$' % static_url
	else:
		static_url = '^(?P<path>.*)$'
	return url(static_url, view, {'document_root': static_root}, name)
