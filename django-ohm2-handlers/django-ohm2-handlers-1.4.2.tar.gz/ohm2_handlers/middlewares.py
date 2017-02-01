from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from . import utils as h_utils
from . import settings as h_settings


class HandlersMiddleware(object):
	
	def process_request(self, request):
		
		request.context = {}
		
		return None
	
	
	def process_response(self, request, response):

		h_utils.update_statistics(request, response)

		return response




class BlockedIpMiddleware(object):
	
	def process_request(self, request):
		
		if request.META.get('REMOTE_ADDR') in h_settings.BLOCKED_IPS:
			return HttpResponseForbidden('<h1>Forbidden</h1>')
		
		return None
	
	
	def process_response(self, request, response):

		h_utils.update_statistics(request, response)

		return response		
	
