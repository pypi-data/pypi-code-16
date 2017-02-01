from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from . import utils



class SocialstatisticsMiddlewares(object):
	
	def process_request(self, request):
		
		request.context['c_socialstatistics'] = {}
		
		if request.user.is_authenticated():

			is_staff = request.user.is_staff
			is_superuser = request.user.is_superuser
			
			if is_superuser or is_staff:
				return None

				
		return None
	
	
	def process_response(self, request, response):
		
		return response
	
