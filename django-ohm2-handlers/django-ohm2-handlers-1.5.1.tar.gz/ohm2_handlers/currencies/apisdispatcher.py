from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from ohm2_handlers import utils as h_utils
#from ohm2_handlers.accounts import utils as accounts_utils
from . import settings
from . import utils as currencies_utils
from . import serializers as currencies_serializers
from . import errors as currencies_errors
from .decorators import currencies_safe_request
from .definitions import CurrenciesRunException, CurrenciesMethodException
import simplejson as json
import os, time, random, datetime


@currencies_safe_request
def view_base(request, version, method, function, keys):
	if request.method == method:
		params, holder = {"request" : request, "version" : version}, getattr(request, method)
		for o in keys:
			params[o[0]] = holder.get(o[1],o[2])
		return function(params)
	raise CurrenciesMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


@currencies_safe_request
def view_base_json(request, version, method, function, keys):
	if request.method == method:
		try:
			holder = json.loads(request.body)
		except ValueError:
			return {"error" : {"code" : -1, "message": "Invalid JSON object"}}
		params = {"request" : request, "version" : version}
		for o in keys:
			params[o[0]] = holder.get(o[1],o[2])
		return function(params)
	raise CurrenciesMethodException(request.method, request.META.get("REMOTE_ADDR", ""))	


@currencies_safe_request
def view_base_data(request, version, method, function, keys):
	if request.method == method:
		params = {"request" : request, "version" : version}
		for o in keys:
			params[o[0]] = request.data.get(o[1],o[2])
		return function(params)
	raise CurrenciesMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


def index(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
					 	))
	
	request = p["request"]
	#user = accounts_utils.get_user(username = request.user.get_username())
	
	res = {
	}
	return res