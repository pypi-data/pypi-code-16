import urlparse

from django.http import HttpResponse

def enable_cors(origins, methods, allow_credentials):
	"""Enable Cross-origin resource sharing on a view, by responding to pre-flight requests and adding appropriate headers.

	origins - a list of allowed hostnames, or empty or None for all hostnames
	methods - a list of allowed methods in caps, or copy the requests method if None
	allow_credentials - allow the client to pass cookies

	http://www.html5rocks.com/en/tutorials/cors/
	http://www.w3.org/TR/cors/
	https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS
	"""
	def enable_cors_decorator(func):
		def enable_cors_fun(request, *args, **kwargs):
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
		return enable_cors_fun
	return enable_cors_decorator
