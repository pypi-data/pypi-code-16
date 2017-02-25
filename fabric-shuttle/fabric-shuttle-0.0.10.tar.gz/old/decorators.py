import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.http.request import validate_host

def require_superuser(func):
	"""Limit view to superusers only."""
	def require_superuser_fun(request, *args, **kwargs):
		if not request.user.is_superuser or not request.user.is_active:
			return redirect_to_login(request.get_full_path())
		return func(request, *args, **kwargs)
	return require_superuser_fun

def require_staff(func):
	"""Limit view to staff only.
	
	The django.contrib.admin.views.decorators.staff_member_required decorator will only redirect to the admin login page.
	"""
	def require_staff_fun(request, *args, **kwargs):
		if not request.user.is_staff or not request.user.is_active:
			return redirect_to_login(request.get_full_path())
		return func(request, *args, **kwargs)
	return require_staff_fun

def require_superuser_403(func):
	"""Limit view to superusers only or raise a 403."""
	def require_superuser_fun(request, *args, **kwargs):
		if not request.user.is_superuser or not request.user.is_active:
			raise PermissionDenied()
		return func(request, *args, **kwargs)
	return require_superuser_fun

def require_staff_403(func):
	"""Limit view to staff only or raise a 403."""
	def require_staff_fun(request, *args, **kwargs):
		if not request.user.is_staff or not request.user.is_active:
			raise PermissionDenied()
		return func(request, *args, **kwargs)
	return require_staff_fun

def require_referer(*netlocs):
	"""Limit a view to a specific list of referers. If unspecified, settings.ALLOWED_HOSTS is used."""
	def require_referer_decorator(func):
		def require_referer_fun(request, *args, **kwargs):
			if settings.DEBUG:
				return func(request, *args, **kwargs)
			referer = request.META.get('HTTP_REFERER', '')
			if not netlocs:
				if len(settings.ALLOWED_HOSTS):
					if validate_host(urlparse.urlparse(referer).netloc, settings.ALLOWED_HOSTS):
						return func(request, *args, **kwargs)
			else:
				if urlparse.urlparse(referer).netloc in netlocs:
					return func(request, *args, **kwargs)
			raise PermissionDenied()
		return require_referer_fun
	return require_referer_decorator

def require_https(func):
	"""Redirect to https if the view is being requested with http."""
	def require_https_fun(request, *args, **kwargs):
		if settings.DEBUG:
			return func(request, *args, **kwargs)
		if not request.is_secure():
			request_url = request.build_absolute_uri(request.get_full_path())
			secure_url = request_url.replace('http://', 'https://')
			return HttpResponsePermanentRedirect(secure_url)
		return func(request, *args, **kwargs)
	return require_https_fun

# when using with toastr.js, all types are supported besides debug
# this can be overriden https://docs.djangoproject.com/en/dev/ref/contrib/messages/
def add_message(level, message):
	"""Add a message to a view."""
	def add_message_decorator(func):
		def add_message_fun(request, *args, **kwargs):
			messages.add_message(request, level, message)
			return func(request, *args, **kwargs)
		return add_message_fun
	return add_message_decorator

def require_basic_auth(username, password, realm):
	"""Requires the browser to do basic authentication with the user/password pair specified."""
	def require_basic_auth_decorator(func):
		def require_basic_auth_fun(request, *args, **kwargs):
			if request.META.has_key('HTTP_AUTHORIZATION'):
				auth = [i for i in request.META['HTTP_AUTHORIZATION'].split(' ') if i]
				if auth[0].lower() == 'basic' and auth[1].decode('base64') == '%s:%s' % (username, password):
					return func(request, *args, **kwargs)
			response = HttpResponse(status=401)
			response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
			return response
		return require_basic_auth_fun
	return require_basic_auth_decorator
