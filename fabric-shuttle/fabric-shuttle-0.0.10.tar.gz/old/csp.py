import urlparse

from django.http import HttpResponse

def enable_csp(origins, methods, allow_credentials):
	"""Enable the Content Security Policy header for a view.

	NOTE: Setting a CSP does not allow cross-domain requests, CORS is still needed.

	origins - a list of allowed hostnames, or empty or None for all hostnames
	methods - a list of allowed methods in caps, or copy the requests method if None
	allow_credentials - allow the client to pass cookies

	http://www.html5rocks.com/en/tutorials/cors/
	http://www.w3.org/TR/cors/
	"""
	def enable_csp_decorator(func):
		def enable_csp_fun(request, *args, **kwargs):
			# Only handle if the Origin header is present
			if not request.META.has_key('HTTP_ORIGIN'):
				return func(request, *args, **kwargs)
			if request.method == 'OPTIONS':
				if origins and urlparse.urlparse(request.META['HTTP_ORIGIN']).netloc not in origins:
					return HttpResponse(status=403)
				if methods and request.META.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD', 'GET') not in methods:
					return HttpResponse(status=405)
				response = HttpResponse(status=204)
			else:
				response = func(request, *args, **kwargs)
			# Copy the request's Origin
			response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
			# Set the allowed methods
			if methods:
				response['Access-Control-Allow-Methods'] = ', '.join(methods)
			else:
				response['Access-Control-Allow-Methods'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD', 'GET, POST, UPDATE, DELETE')
			# Copy the request's Access-Control-Request-Headers
			if request.META.has_key('HTTP_ACCESS_CONTROL_REQUEST_HEADERS'):
				response['Access-Control-Allow-Headers'] = request.META['HTTP_ACCESS_CONTROL_REQUEST_HEADERS']
			if allow_credentials:
				response['Access-Control-Allow-Credentials'] = 'true'
			return response
		return enable_csp_fun
	return enable_csp_decorator
