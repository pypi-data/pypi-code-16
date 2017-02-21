from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from ohm2_handlers import utils as h_utils
from ohm2_handlers.accounts import utils as accounts_utils
from . import settings
from . import utils as socialstatistics_utils
from . import serializers as socialstatistics_serializers
from . import errors as socialstatistics_errors
from .decorators import socialstatistics_safe_request
from .definitions import SocialstatisticsRunException, SocialstatisticsMethodException
import simplejson as json
import facebook as facebook_sdk
import tweepy
import os, time, random, datetime, requests


@socialstatistics_safe_request
def view_base(request, version, method, function, keys):
	if request.method == method:
		params, holder = {"request" : request, "version" : version}, getattr(request, method)
		for o in keys:
			params[o[0]] = holder.get(o[1],o[2])
		return function(params)
	raise SocialstatisticsMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


@socialstatistics_safe_request
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
	raise SocialstatisticsMethodException(request.method, request.META.get("REMOTE_ADDR", ""))	


@socialstatistics_safe_request
def view_base_data(request, version, method, function, keys):
	if request.method == method:
		params = {"request" : request, "version" : version}
		for o in keys:
			params[o[0]] = request.data.get(o[1],o[2])
		return function(params)
	raise SocialstatisticsMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


def twitter_authorization_url(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
					 	))
	
	request = p["request"]

	args = (settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
	if settings.TWITTER_AUTHORIZED_URL:
		args += (settings.WEBSITE_URL + reverse("socialstatistics:api_twitter_get_access_token", kwargs = {"version" : "1"}),)

	auth = tweepy.OAuthHandler(*args)
	

	try:
		redirect_url = auth.get_authorization_url()
	except tweepy.TweepError as e:
		return {"error" : SocialstatisticsRunError(**SocialstatisticsErrors.TWITTER_AUTHORIZATION_URL_FAILED).regroup()}


	request.session["twitter_request_token"] = auth.request_token

	res = {
		"error" : None,
		"ret" : redirect_url,
	}
	return res



def twitter_get_access_token(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "oauth_token", 1),
							("string", "oauth_verifier", 1),
					 	))
	
	request = p["request"]

	user = accounts_utils.get_user(username = request.user.get_username())

	auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
	
	request_token = request.session.get("twitter_request_token", None)
	if request_token is None:
		return {"error" : SocialstatisticsRunError(**SocialstatisticsErrors.TWITTER_INVALID_REQUEST_TOKEN).regroup()}
	
	elif request_token.get("oauth_token") != p["oauth_token"]:
		request_token["oauth_token"] = p["oauth_token"]
		#return {"error" : SocialstatisticsRunError(**SocialstatisticsErrors.TWITTER_INVALID_OAUTH_TOKEN).regroup()}

	auth.request_token = request_token
	

	try:
		auth.get_access_token(p["oauth_verifier"])
	except tweepy.TweepError as e:
		return {"error" : SocialstatisticsRunError(**SocialstatisticsErrors.TWITTER_INVALID_OAUTH_VERIFIER).regroup()}

	
	api = tweepy.API(auth)
	me = api.me()
	name = me.screen_name
	account_id = me.id_str

	twitter = socialstatistics_utils.create_twitter(user, name, account_id, auth.access_token, auth.access_token_secret)

	request.session.pop("twitter_request_token")

	res = {
		"error" : None,
		"ret" : settings.TWITTER_AUTHORIZED_URL,
	}
	return res




def facebook_authorization_url(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
					 	))
	
	request = p["request"]

	user = accounts_utils.get_user(username = request.user.get_username())

	redirect_url = settings.FACEBOOK_LOGIN_DIALOG_URL
	redirect_url += "client_id=" + settings.FACEBOOK_CLIENT_ID
	
	redirect_url += "&state=" + h_utils.random_string(10)
	redirect_url += "&response_type=code"
	redirect_url += "&scope=" + settings.FACEBOOK_SCOPE
	redirect_url += "&redirect_uri=" + settings.WEBSITE_URL + reverse("socialstatistics:api_facebook_get_access_token", kwargs = {"version" : "1"})
	
	res = {
		"error" : None,
		"ret" : redirect_url,
	}
	return res


def facebook_get_access_token(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "code", 1),
					 	))
	
	request = p["request"]

	user = accounts_utils.get_user(username = request.user.get_username())

	url = settings.FACEBOOK_GET_ACCESS_TOKEN_URL
	url += "client_id=" + settings.FACEBOOK_CLIENT_ID
	url += "&redirect_uri=" + settings.WEBSITE_URL + reverse("socialstatistics:api_facebook_get_access_token", kwargs = {"version" : "1"})
	url += "&client_secret=" + settings.FACEBOOK_APP_SECRET
	url += "&code=" + p["code"]

	response = requests.get(url)
	if response.status_code != 200:
		return {"error" : SocialstatisticsRunError(**SocialstatisticsErrors.FACEBOOK_INVALID_ACCESS_TOKEN_REQUEST).regroup()}

	ret = response.json()
	
	error = ret.get("error")
	if error:
		return {"error" : error}

	access_token = ret.get("access_token")
	token_type = ret.get("token_type")
	expires_in = ret.get("expires_in")


	if access_token is None or token_type is None:
		return {"error" : SocialstatisticsRunError(**SocialstatisticsErrors.FACEBOOK_INVALID_ACCESS_TOKEN).regroup()}	

	
	if expires_in:
		expiration = timezone.now() + relativedelta(seconds = +expires_in)
	else:
		expiration = None	

	graph = facebook_sdk.GraphAPI(access_token = access_token)
	me = graph.get_object(id = "me")

	facebook = socialstatistics_utils.create_facebook(user, me.get("name", ""), me["id"], access_token, token_type, expiration = expiration)

	res = {
		"error" : None,
		"ret" : settings.FACEBOOK_REDIRECT_URI,
	}
	return res



def twitter_delete_account(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "identity", 1),
					 	))
	
	request = p["request"]

	user = accounts_utils.get_user(username = request.user.get_username())

	twitter = socialstatistics_utils.get_twitter(user = user, identity = p["identity"], deleted = False)

	socialstatistics_utils.delete_twitter(twitter)

	res = {
		"error" : None,
		"ret" : True,
	}
	return res



def facebook_delete_account(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "identity", 1),
					 	))
	
	request = p["request"]

	user = accounts_utils.get_user(username = request.user.get_username())

	facebook = socialstatistics_utils.get_facebook(user = user, identity = p["identity"], deleted = False)

	socialstatistics_utils.delete_facebook(facebook)

	res = {
		"error" : None,
		"ret" : True,
	}
	return res


def facebook_delete_page(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "identity", 1),
					 	))
	
	request = p["request"]

	user = accounts_utils.get_user(username = request.user.get_username())

	page = socialstatistics_utils.get_facebookpage(facebook__user = user, identity = p["identity"], deleted = False)

	socialstatistics_utils.delete_facebookpage(page)

	res = {
		"error" : None,
		"ret" : True,
	}
	return res	



def facebook_create_page(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "facebook", 1),
							("string", "page_id", 1),
					 	))
	
	request = p["request"]

	user = accounts_utils.get_user(username = request.user.get_username())

	facebook = socialstatistics_utils.get_facebook(user = user, identity = p["facebook"], deleted = False)

	raw_pages = facebook.get_object(id = 'me/accounts')["data"]
	for raw_page in raw_pages:
		if raw_page["id"] == p["page_id"]:
			break
	else:
		return {"error" : SocialstatisticsRunError(**SocialstatisticsErrors.FACEBOOK_INVALID_PAGE_ID).regroup()}

	facebookpage = socialstatistics_utils.create_facebookpage(facebook, raw_page["name"], raw_page["id"])	

	res = {
		"error" : None,
		"ret" : True,
	}
	return res