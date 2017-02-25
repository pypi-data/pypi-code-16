import os
try:
	from urllib.parse import unquote
except ImportError:
	from urllib import unquote

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.static import serve

from .decorators import require_referer
from .middleware import AssumeMiddleware

@require_referer()
def iplocation(request):
	"""Resolves the users's remote address into a location.
	
	Returns with a callback and argument similar to what is expected from navigator.geolocation.getCurrentPosition()
	"""
	from django.contrib.gis.geoip import GeoIP
	loc = None
	if request.META.has_key('REMOTE_ADDR'):
		loc = GeoIP().lat_lon(request.META['REMOTE_ADDR'])
	if loc:
		return HttpResponse("iplocationLoaded({'coords':{'latitude': %f, 'longitude': %f}});" % loc, content_type='text/javascript')
	else:
		return HttpResponse("iplocationLoaded(null);", content_type='text/javascript')

@require_POST
@csrf_exempt
def session_cross_subdomain(request):
	"""Cross a session over from one subdomain to another, where session backends are shared. Require a POST so that sessionid doesn't get logged anywhere."""
	next = request.POST.get('next', None)
	if next:
		response = HttpResponseRedirect(next)
	else:
		response = HttpResponse()
	if request.POST.has_key('sessionid'):
		response.set_cookie('sessionid', request.POST['sessionid'])
	return response

def webapp_serve(request, path, document_root=None):
	"""View for debugging (runwebapp), adds index.html to whatever path if needed. Will try to resolve static files when STATIC_URL prefix is missing."""
	index = settings.WEBAPP_INDEX if hasattr(settings, 'WEBAPP_INDEX') else 'index.html'
	if path.endswith('/'):
		return serve(request, path + index, document_root)
	else:
		# Determine if path is directory
		path = os.path.normpath(unquote(path))
		path = path.lstrip('/')
		fullpath = os.path.join(document_root, path)	
		if os.path.isdir(fullpath):
			return serve(request, path + '/' + index, document_root)
		else:
			try:
				return serve(request, path, document_root)
			except Http404 as e:
				result = finders.find(path)
				if not result:
					raise e
				else:
					result = result[0] if isinstance(result, (list, tuple)) else result
					return serve(request, path, result[:-len(path)])
