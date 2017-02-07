from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from ohm2_handlers import utils as h_utils
from . import settings
from . import utils as accounts_utils
from . import serializers as accounts_serializers
from . import errors as accounts_errors
from .decorators import accounts_safe_request
from .definitions import AccountsRunException, AccountsMethodException
import simplejson as json
import os, time, random, datetime


@accounts_safe_request
def view_base(request, version, method, function, keys):
	if request.method == method:
		params, holder = {"request" : request, "version" : version}, getattr(request, method)
		for o in keys:
			params[o[0]] = holder.get(o[1],o[2])
		return function(params)
	raise AccountsMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


@accounts_safe_request
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
	raise AccountsMethodException(request.method, request.META.get("REMOTE_ADDR", ""))	


@accounts_safe_request
def view_base_data(request, version, method, function, keys):
	if request.method == method:
		params = {"request" : request, "version" : version}
		for o in keys:
			params[o[0]] = request.data.get(o[1],o[2])
		return function(params)
	raise AccountsMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


def signup(params):
	p = h_utils.mix_cleaned_data(params,
								 (
									("request", "request", ""),
									("string", "version", 1),
									("string", "username", 1),
									("string", "password", 1),
									("string", "email", 0),
								 ))
	

	request = p["request"]

	if request.user.is_authenticated():
		return {"error" : AccountsRunException(**accounts_errors.USER_ALREADY_LOGGED_IN).regroup()}

	
	if settings.SIGNUP_USERNAME_TRUNCATION:
		p["username"] = p["username"][:settings.MAX_USERNAME_LENGTH]
			

	if len(p["username"]) > settings.MAX_USERNAME_LENGTH:
		return {"error": AccountsRunException(**accounts_errors.USERNAME_TOO_LONG).regroup()}

	elif accounts_utils.user_exist(username = p["username"]):
		return {"error" : AccountsRunException(**accounts_errors.USER_ALREADY_EXIST).regroup()}

	elif settings.CHECK_PASSWORD_SECURE and not accounts_utils.is_password_secure(p["password"]):
		return {"error" : AccountsRunException(**accounts_errors.THE_PASSWORD_IS_NOT_SECURE).regroup()}

	elif len(p["email"]) > 0 and not h_utils.is_email_valid(p["email"]):
		return {"error" : AccountsRunException(**accounts_errors.INVALID_EMAIL).regroup()}

	elif not settings.SIGNUPS_ENABLED:
		return {"error" : AccountsRunException(**accounts_errors.SIGNUPS_DISABLED).regroup()}

	elif settings.PRESIGNUPS_ENABLED:
		return {"error" : AccountsRunException(**accounts_errors.PRESIGNUPS_ENABLED).regroup()}

	if len(p["email"]) == 0 and h_utils.is_email_valid(p["username"]):
		p["email"] = p["username"]

	
	user = accounts_utils.create_user(p["username"], p["email"], p["password"])
	try:
		
		user = accounts_utils.run_signup_pipeline(user, request)

	except Exception as e:
		h_utils.db_delete(user)

		code = accounts_errors.SIGNUP_PIPELINE_FAILED["code"]
		message = accounts_errors.SIGNUP_PIPELINE_FAILED["message"]
		extra = "{0}".format(e)

		return {"error" : AccountsRunException(code = code, message = message, extra = extra).regroup()}



	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret


def signup_and_get_token(params):
	res = signup(params)
	if res["error"] or not res["ret"]:
		return res

	username = params["username"].strip()
	if settings.SIGNUP_USERNAME_TRUNCATION:
		username = username[:settings.MAX_USERNAME_LENGTH]
		
	user = accounts_utils.get_user_or_none(username = username)		
	token = accounts_utils.get_or_create_authtoken(user)	
	
	res = {
		"error" : None,
		"ret" : {
			"token" : token.key,
		}
	}
	return res


def facebook_signup(params):
	p = h_utils.mix_cleaned_data(params, (
									("request", "request", ""),
									("string", "version", 1),
									("string", "access_token", 10),
									#("email", "email", ""),
								 ))
	
	try:
		graph = facebook.GraphAPI(access_token = p["access_token"])
	except Exception as e:
		return {"error" : AccountsRunException(**accounts_errors.INVALID_FACEBOOK_ACCESS_TOKEN).regroup()}
	

	try:
		me = graph.get_object(id = 'me?fields=email')
	except Exception as e:
		
		if hasattr(e, "message"):
			
			if e.message.find("Error validating access token: Session has expired") > -1:
				return {"error" : AccountsRunException(**accounts_errors.FACEBOOK_EXPIRED_ACCESS_TOKEN).regroup()}
			

		return {"error" : AccountsRunException(**accounts_errors.FACEBOOK_CONNECTION_ERROR).regroup()}	
		
	
	email = me.get("email")
	if email is None:
		return {"error" : AccountsRunException(**accounts_errors.FACEBOOK_EMAIL_PERMISSION_NOT_SETTED).regroup()}

	user = accounts_utils.get_or_none_user(email = email)
	if user:
		res = {
			"error" : None,
			"ret" : True,
		}
		return res


	signup_params = {
		"request" : p["request"],
		"version" : p["version"],
		"username" : email,
		"password" : h_utils.random_string(15),
		"email" : email,
	}

	return signup(signup_params)



def facebook_signup_and_get_token(params):
	res = facebook_signup(params)
	if res["error"] or not res["ret"]:
		return res

	graph = facebook.GraphAPI(access_token = params["access_token"])
	me = graph.get_object(id = 'me?fields=email')
	email = me["email"]

	user = accounts_utils.get_user_or_none(email = email)		
	token = accounts_utils.get_or_create_authtoken(user)	
	
	res = {
		"error" : None,
		"ret" : {
			"token" : token.key,
		}
	}
	return res


def login(params):
	p = h_utils.cleaned(params, (						
							("request", "request", ""),
							("string", "version", 1),
							("string", "username", 1),
							("string", "password", 1),
						))
	
	
	request = p["request"]

	if request.user.is_authenticated():
		return {"error": None, "ret" : True}

	username, password = p["username"], p["password"]
	if settings.LOGIN_USERNAME_TRUNCATION:
		username = username[:settings.MAX_USERNAME_LENGTH]


	if not settings.ENABLE_EMAIL_LOGIN and h_utils.is_email_valid(username) and not settings.ENABLE_ALIAS_LOGIN:
		return {"error" : AccountsRunException(**accounts_errors.EMAIL_LOGIN_DISABLED).regroup()}

	elif settings.ENABLE_EMAIL_LOGIN and h_utils.is_email_valid(username) and accounts_utils.user_exist(email = username) and settings.UNIQUE_USER_EMAILS:
		user = accounts_utils.get_user(email = username)
		auth_user = accounts_utils.user_authenticate(user.get_username(), password)
	
	elif settings.ENABLE_ALIAS_LOGIN:
		
		alias = accounts_utils.get_or_none_alias(name = username)
		if alias:
			auth_user = accounts_utils.user_authenticate(alias.user.get_username(), password)
		else:
			auth_user = None

	else:

		auth_user = accounts_utils.user_authenticate(username, password)
	

	
	if auth_user is None:
		return {"error" : AccountsRunException(**accounts_errors.WRONG_CREDENTIALS).regroup()}

		
	accounts_utils.run_login_pipeline(request, auth_user)


	res = {
		"error" : None,
		"ret" : True,
	}
	return res



def login_and_get_token(params):
	res = login(params)
	if res["error"] or not res["ret"]:
		return res

	username = params["username"].strip()
	if settings.LOGIN_USERNAME_TRUNCATION:
		username = username[:settings.MAX_USERNAME_LENGTH]

	user = accounts_utils.get_user_or_none(username = username)		
	token = accounts_utils.get_or_create_authtoken(user)	
	
	res = {
		"error" : None,
		"ret" : {
			"token" : token.key,
		}
	}
	return res

def logout(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
						))


	request = p["request"]

	
	if not request.user.is_authenticated():
		return {"error": None, "ret" : False}

	
	accounts_utils.run_logout_pipeline(request)

	
	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret

def change_password(params):
	p = h_utils.cleaned(params, (
						
							("request", "request", ""),
							("string", "version", 1),
							("string", "current", 1),
							("string", "password", 1),
						))

	if not p["request"].user.is_authenticated():
		return {"error": None, "ret" : False}

	user = accounts_utils.get_user_or_none(username = p["request"].user.get_username())
	if user is None:
		return {"error": None, "ret" : False}

	elif not user.check_password(p["current"]):
		return {"error" : AccountsRunException(**accounts_errors.INVALID_CURRENT_PASSWORD).regroup()}

	elif settings.CHECK_PASSWORD_SECURE and not accounts_utils.is_password_secure(p["password"], user):
		return {"error" : AccountsRunException(**accounts_errors.THE_PASSWORD_IS_NOT_SECURE).regroup()}

	user = accounts_utils.change_password(user, p["password"])
	
	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret

def reset_password_step_1(params):
	p = h_utils.cleaned(params, (
						
							("request", "request", ""),
							("string", "version", 1),
							("string", "username", 1),
						))

	request = p["request"]
	if request.user.is_authenticated():
		return {"error": None, "ret" : False}

	username = p["username"]
	
	user = accounts_utils.get_user_or_none(username = username)
	if user is None and not settings.ENABLE_EMAIL_LOGIN:
		return {"error": None, "ret" : False}
	
	elif settings.ENABLE_EMAIL_LOGIN and h_utils.is_email_valid(username) and settings.UNIQUE_USER_EMAILS:
		user = accounts_utils.get_user_or_none(email = username)
		if user == None:
			return {"error": None, "ret" : False}

	passwordreset = accounts_utils.get_or_create_passwordreset(user, request)
	
	sent = False
	if passwordreset.send_again() and settings.PASSWORD_RESET_SEND_ENABLE:


		passwordreset = accounts_utils.send_passwordreset(passwordreset, request)
		sent = True
		

	ret = {
		"error" : None,
		"ret" : sent,
	}
	return ret


def reset_password_step_2(params):
	p = h_utils.cleaned(params, (						
							("request", "request", ""),
							("string", "version", 1),
							("string", "identity", 0),
							("string", "code", 0),
							("email", "email", ""),
							("string", "password", 1),
						))

	request = p["request"]
	if request.user.is_authenticated():
		return {"error": None, "ret" : False}

	if len(p["identity"]) > 0:
		passwordreset = accounts_utils.get_passwordreset_or_none(identity = p["identity"], user__email = p["email"])
	
	elif len(p["code"]) > 0:
		passwordreset = accounts_utils.get_passwordreset_or_none(code = p["code"], user__email = p["email"])

	else:
		return {"error" : AccountsRunException(**accounts_errors.INVALID_PASSWORD_RESET).regroup()}

	
	if passwordreset is None:
		return {"error" : AccountsRunException(**accounts_errors.INVALID_PASSWORD_RESET).regroup()}

	elif passwordreset.last_sent_date == None:
		return {"error" : AccountsRunException(**accounts_errors.INVALID_PASSWORD_RESET).regroup()}

	elif passwordreset.activation_date != None:
		return {"error" : AccountsRunException(**accounts_errors.PASSWORD_RESET_ALREADY_ACTIVATED).regroup()}

	elif settings.CHECK_PASSWORD_SECURE and not accounts_utils.is_password_secure(p["password"]):
		return {"error" : AccountsRunException(**accounts_errors.THE_PASSWORD_IS_NOT_SECURE).regroup()}

	
	passwordreset = accounts_utils.change_password_with_passwordreset(passwordreset, p["password"])
	
	login_params = {
		"request" : request,
		"version" : p["version"],
		"username" : passwordreset.user.get_username(),
		"password" : p["password"],
	}
	
	login(login_params)

	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret




@accounts_safe_request
def view_update_avatars(request, version):
	if request.method == "POST":
		params = {
			"request" : request,
			"version" : version,
			"original" : request.FILES["img"],
		}
		return update_avatars(params)
	raise AccountsMethodException(request.method, request.META.get("REMOTE_ADDR", ""))



def update_avatars(params):
	p = h_utils.cleaned(params, (
						
							("request", "request", ""),
							("string", "version", 1),
							("u_file", "original", None),
						))

	request = p["request"]
	
	user = accounts_utils.get_user(username = request.user.get_username())

	avatars = accounts_utils.get_or_none_avatars(user = user)
	if avatars:
		avatars = accounts_utils.update_avatars(avatars, original = p["original"])
	else:
		avatars = accounts_utils.create_avatars(user, original = p["original"])


	ret = {
		"error" : None,
		"ret" : {
			"ori" : os.path.join(settings.MEDIA_URL, avatars.original.name),
			"o_75x75" : avatars.o_75x75.url,
			"o_100x100" : avatars.o_100x100.url,
			"o_125x125" : avatars.o_125x125.url,
			"o_150x150" : avatars.o_150x150.url,
			"o_200x200" : avatars.o_200x200.url,
		},
	}
	return ret


def update_settings(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "country", 0),
							("string", "currency", 0),
							("string", "timezone", 0),
							("string", "language", 0),
						))

	request = p["request"]
	
	user = accounts_utils.get_user(username = request.user.get_username())

	user_settings = accounts_utils.get_settings(user = user)
	
	kwargs = {}
	
	if len(p.get("country", "")):
		kwargs["country"] = countries_utils.get_country(code = p["country"])

	if len(p.get("currency", "")):
		kwargs["currency"] = currencies_utils.get_currency(code = p["currency"])	

	if p.get("timezone", "invalid-timezone") in accounts_utils.get_timezones():
		kwargs["timezone"] = p["timezone"]

	if p.get("language", "invalid-language") in [lang[0] for lang in accounts_utils.get_languages()]:
		kwargs["language"] = p["language"]
		accounts_utils.activate_language(p["request"], p.get("language"))
		
	user_settings = accounts_utils.update_settings(user_settings, **kwargs)
	request.session['tz'] = user_settings.timezone
	

	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret



def update_user_password(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),		
							("string", "current_password", 1),
							("string", "new_password", 1),
						))

	request = p["request"]
	
	user = accounts_utils.get_user(username = request.user.get_username())

	if not user.check_password(p["current_password"]):
		return {"error" : AccountsRunException(**accounts_errors.INVALID_CURRENT_PASSWORD).regroup()}
	
	elif settings.CHECK_PASSWORD_SECURE and not accounts_utils.is_password_secure(p["new_password"], user = user):
		return {"error" : AccountsRunException(**accounts_errors.THE_PASSWORD_IS_NOT_SECURE).regroup()}

	user = accounts_utils.change_password(user, p["new_password"])	

	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret


def presignup_step_one(params, **kwargs):
	p = h_utils.mix_cleaned_data(params,
								 (
									("request", "request", ""),
									("string", "version", 1),
									("email", "email", ""),
								 ))
	
	if p["request"].user.is_authenticated():
		return {"error" : AccountsRunException(**accounts_errors.USER_ALREADY_LOGGED_IN).regroup()}

	elif not h_utils.is_email_valid(p["email"]):
		return {"error" : AccountsRunException(**accounts_errors.INVALID_EMAIL).regroup()}

	elif not settings.SIGNUPS_ENABLED:
		return {"error" : AccountsRunException(**accounts_errors.SIGNUPS_DISABLED).regroup()}

	elif not settings.PRESIGNUPS_ENABLED:
		return {"error" : AccountsRunException(**accounts_errors.PRESIGNUPS_DISABLED).regroup()}

	presignup = accounts_utils.get_or_none_presignup(email = p["email"], activation_date = None)
	if presignup is None:
		presignup = accounts_utils.create_presignup(p["email"])
	
	
	send_presignup_kwargs = {}
	template_path = kwargs.get("template_path", None)
	if template_path:
		send_presignup_kwargs["template_path"] = template_path

	
	if presignup.send_again() and kwargs.get("sent_presignup", True) is True:
		presignup = accounts_utils.send_presignup(presignup, p["request"], **send_presignup_kwargs)




	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret



def presignup_step_two(params):
	p = h_utils.mix_cleaned_data(params,
								 (
									("request", "request", ""),
									("string", "version", 1),
									("string", "identity", 10),
									("string", "username", 1),
									("string", "password", 1),
									("string", "email", 0),
								 ))
	
	if p["request"].user.is_authenticated():
		return {"error" : AccountsRunException(**accounts_errors.USER_ALREADY_LOGGED_IN).regroup()}

	elif len(p["username"]) > settings.MAX_USERNAME_LENGTH:
		return {"error": AccountsRunException(**accounts_errors.USERNAME_TOO_LONG).regroup()}

	elif accounts_utils.user_exist(username = p["username"]):
		return {"error" : AccountsRunException(**accounts_errors.USER_ALREADY_EXIST).regroup()}

	elif settings.CHECK_PASSWORD_SECURE and not accounts_utils.is_password_secure(p["password"]):
		return {"error" : AccountsRunException(**accounts_errors.THE_PASSWORD_IS_NOT_SECURE).regroup()}

	elif len(p["email"]) > 0 and not h_utils.is_email_valid(p["email"]):
		return {"error" : AccountsRunException(**accounts_errors.INVALID_EMAIL).regroup()}

	elif not settings.SIGNUPS_ENABLED:
		return {"error" : AccountsRunException(**accounts_errors.SIGNUPS_DISABLED).regroup()}

	elif not settings.PRESIGNUPS_ENABLED:
		return {"error" : AccountsRunException(**accounts_errors.PRESIGNUPS_DISABLED).regroup()}


	if len(p["email"]) == 0 and h_utils.is_email_valid(p["username"]):
		p["email"] = p["username"]
			
		
	presignup = accounts_utils.get_presignup(identity = p["identity"])
	if presignup.activation_date:
		return {"error" : AccountsRunException(**accounts_errors.PRESIGNUP_ALREADY_ACTIVATED).regroup()}

	
	user = accounts_utils.create_user(p["username"], p["email"], p["password"])
	try:
		
		user = accounts_utils.run_signup_pipeline(user, request)

	except Exception as e:
		h_utils.db_delete(user)

		code = accounts_errors.SIGNUP_PIPELINE_FAILED["code"]
		message = accounts_errors.SIGNUP_PIPELINE_FAILED["message"]
		extra = "{0}".format(e)

		return {"error" : AccountsRunException(code = code, message = message, extra = extra).regroup()}

		

	try:
		presignup = accounts_utils.activate_presignup(presignup)
	except Exception as e:
		h_utils.db_delete(user)
		return {"error" : AccountsRunException(**accounts_errors.PRESIGNUPS_FAILED).regroup()}

		
	

	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret



def update_user_information(params):
	p = h_utils.cleaned(params, (						
							("request", "request", ""),
							("string", "first_name", 0),
							("string", "last_name", 0),
						))

	if not p["request"].user.is_authenticated():
		return {"error" : AccountsRunException(**accounts_errors.USER_NOT_LOGGED_IN).regroup()}

	user = accounts_utils.get_user(username = p["request"].user.get_username())
	
	user = h_utils.db_update(user, first_name = p["first_name"], last_name = p["last_name"])
	
	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret



def update_alias(params):
	p = h_utils.cleaned(params, (						
							("request", "request", ""),
							("string", "name", 1),
						))

	user = accounts_utils.get_user(username = p["request"].user.get_username())
	
	alias = accounts_utils.get_or_none_alias(user = user)
	if alias:

		prev_alias = accounts_utils.get_or_none_alias(name = p["name"])
		if prev_alias and prev_alias.user.get_username() != user.get_username():
			return {"error" : AccountsRunException(**accounts_errors.ALIAS_ALREADY_TAKEN).regroup()}

		alias = h_utils.db_update(alias, name = p["name"])
	else:
		alias = accounts_utils.create_alias(user, p["name"])	
	
	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret