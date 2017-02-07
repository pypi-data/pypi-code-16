from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.db.models import Q
from ohm2_handlers import utils as h_utils
from ohm2_handlers.accounts import utils as accounts_utils
from . import settings
from . import utils as currencies_utils
from .decorators import currencies_safe_request
from .definitions import CurrenciesRunException, CurrenciesMethodException
import os, time, random, datetime


@currencies_safe_request
def view_base(request, method, function, keys):
	if request.method == method:
		params, holder = {"request" : request}, getattr(request, method)
		for o in keys:
			params[o[0]] = holder.get(o[1],o[2])
		return function(params)
	raise CurrenciesMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


def index(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
					 	))
	
	request = p["request"]
	#user = accounts_utils.get_user(username = request.user.get_username())

	ret = {
	}
	return ret