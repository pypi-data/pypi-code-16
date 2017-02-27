from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from ohm2_handlers import utils as h_utils
from . import settings
from . import utils as countries_utils
from .decorators import countries_safe_request
from .definitions import CountriesRunException, CountriesMethodException
from . import serializers as countries_serializers
from . import errors as country_errors
import simplejson as json
import os, time, random, datetime, mimetypes


@countries_safe_request
def view_base(request, version, method, function, keys):
	if request.method == method:
		params, holder = {"request" : request, "version" : version}, getattr(request, method)
		for o in keys:
			params[o[0]] = holder.get(o[1],o[2])
		return function(params)
	raise CountriesMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


@countries_safe_request
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
	raise CountriesMethodException(request.method, request.META.get("REMOTE_ADDR", ""))	


@countries_safe_request
def view_base_data(request, version, method, function, keys):
	if request.method == method:
		params = {"request" : request, "version" : version}
		for o in keys:
			params[o[0]] = request.data.get(o[1],o[2])
		return function(params)
	raise CountriesMethodException(request.method, request.META.get("REMOTE_ADDR", ""))


def flag_code(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "size", 2),
							("string", "filename", 2),
					 	))
	
	if p["size"] in settings.FLAG_SIZES:
		size = p["size"]
	else:
		size = settings.DEFAULT_FLAG_SIZE


	if settings.DEBUG:
		
		filepath = os.path.join(settings.FLAGS_PATH, "iso", size, p["filename"])
		with open(filepath, "rb") as f:
			content = f.read()
		
		mimetype = mimetypes.guess_type(p["filename"])[0]
		content_type = mimetype if mimetype != None else 'image/png'
		response = HttpResponse(content = content, content_type=content_type)
		
	else:
		response = HttpResponse()
		response['X-Accel-Redirect'] = os.path.join(settings.FLAG_URL, "iso", size, p["filename"])
		response['Content-Type'] = ""

		
	

	res = {
		'response' : response,
	}
	return res




def get_country(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "code", 2),
					 	))



	country = countries_utils.get_or_none_country(code = p["code"])
	if country is None:
		return {
			"error" : CountriesRunException( **country_errors.NO_COUNTRY_FOUND ).regroup()
		}

	
	zer = countries_serializers.Country(country, many = False)

	ret = {
		"error" : None,
		"ret" : zer.data
	}
	return ret



def get_regions(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "country", 1),
					 	))



	regions = countries_utils.filter_region(country__code = p["country"])
	zer = countries_serializers.Region(regions, many = True)

	ret = {
		"error" : None,
		"ret" : zer.data
	}
	return ret



def get_provinces(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "region", 1),
					 	))



	provinces = countries_utils.filter_province(region__identity = p["region"])
	zer = countries_serializers.Province(provinces, many = True)

	ret = {
		"error" : None,
		"ret" : zer.data
	}
	return ret



def get_communes(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "region", 1),
					 	))



	communes = countries_utils.filter_commune(province__region__identity = p["region"])
	zer = countries_serializers.Commune(communes, many = True)

	ret = {
		"error" : None,
		"ret" : zer.data
	}
	return ret


def get_user_addresses(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "region", 1),
					 	))

	request = p["request"]

	user = User.object.get(username = request.user.get_username())

	addresses = countries_utils.filter_useraddress(user = user)
	zer = countries_serializers.UserAddress(addresses, many = True)

	ret = {
		"error" : None,
		"ret" : zer.data
	}
	return ret




def create_user_address(params):
	p = h_utils.cleaned(params, (
							("request", "request", ""),
							("string", "version", 1),
							("string", "region", 0),
							("string", "commune", 0),
							("string", "street", 1),
							("string", "number", 1),
							("string", "apartment", 0),
							("string", "extra_information", 0),
							("string", "latitude", 0),
							("string", "longitude", 0),
							("string", "next", 0),
					 	))

	request = p["request"]

	user = User.objects.get(username = request.user.get_username())

	
	kwargs = {
		"apartment" : p["apartment"],
		"extra_information" : p["extra_information"],
	}

	if p["region"]:
		kwargs["region"] = countries_utils.get_or_none_region(identity = p["region"])

	if p["commune"]:
		kwargs["commune"] = countries_utils.get_or_none_commune(identity = p["commune"])

	if p["latitude"]:
		kwargs["latitude"] = float(p["latitude"])

	if p["longitude"]:
		kwargs["longitude"] = float(p["longitude"])	

	address = countries_utils.create_useraddress(user, p["street"], p["number"], **kwargs)
	
	ret = {
		"error" : None,
		"ret" : True,
	}
	return ret