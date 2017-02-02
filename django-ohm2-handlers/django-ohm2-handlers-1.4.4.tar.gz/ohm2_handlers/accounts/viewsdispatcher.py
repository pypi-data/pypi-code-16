from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.db.models import Q
from ohm2_handlers import utils as h_utils
from ohm2_handlers.accounts import utils as accounts_utils
from . import settings
from . import utils as accounts_utils
from .decorators import accounts_safe_request
from .definitions import AccountsRunException, AccountsMethodException
import os, time, random, datetime


@accounts_safe_request
def view_base(request, method, function, keys):
	if request.method == method:
		params, holder = {"request" : request}, getattr(request, method)
		for o in keys:
			params[o[0]] = holder.get(o[1],o[2])
		return function(params)
	raise AccountsMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


def logout(params):
	p = h_utils.mix_cleaned_data(params,
								 (
									("request", "request", ""),
								 ))
	
	
	accounts_utils.run_logout_pipeline(p["request"])
	
	ret = {
		"error" : None
	}
	return ret



def presignup_step_one(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("email", "email", ""),
					 	))


	request = p["request"]
	
	### Fix this later for iOS and Android if neccesary
	device = "default"



	api_params = {
		"request" : request,
		"device" : device,
		"email" : p["email"],
	}
	res = accounts_apisdispatcher.presignup_step_one(api_params)
	error = True if res["error"] else False
	assert not error == True

	presignup = accounts_utils.get_presignup(email = p["email"])

	ret = {
		"presignup" : presignup,
	}	
	return ret


@accounts_safe_request
def view_presignup_step_two(request):
	if request.method == "GET":
		params = {
			"request" : request,
			"identity" : request.GET["ide"],
			"email" : request.GET["e"],
		}
		return presignup_step_two_get(params)

	elif request.method == "POST":
		params = {
			"request" : request,
			"identity" : request.POST["ide"],
			"password" : request.POST["password"],
		}
		return presignup_step_two_post(params)

	raise RootMethodError(app = "root", message = "wrong method: {0}".format(request.method))

def presignup_step_two_get(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "identity", 10),
							("email", "email", ""),
					 	))

	presignup = accounts_utils.get_presignup(identity = p["identity"])

	ret = {
		"presignup" : presignup,
	}	
	return ret


def presignup_step_two_post(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "identity", 10),
							("string", "password", 1),
					 	))


	presignup = accounts_utils.get_presignup(identity = p["identity"])


	request = p["request"]
	### Fix this later for iOS and Android if neccesary
	device = "default"


	api_params = {
		"request" : request,
		"device" : device,
		"identity" : presignup.identity,
		"username" : presignup.email,
		"password" : p["password"],
		"email" : presignup.email,
	}
	res = accounts_apisdispatcher.presignup_step_two(api_params)
	error = True if res["error"] else False
	assert not error == True

	presignup = accounts_utils.get_presignup(identity = p["identity"])

	ret = {
		"presignup" : presignup,
	}	
	return ret


def check_user_integrity_and_redirect(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "next", 1),
					 	))

	user = accounts_utils.get_user(username = p["request"].user.get_username())
	accounts_utils.check_user_integrity(user)

	ret = {
		"next" : p["next"],
	}	
	return ret