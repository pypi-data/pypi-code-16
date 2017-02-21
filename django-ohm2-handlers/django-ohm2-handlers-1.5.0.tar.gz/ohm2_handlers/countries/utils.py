from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers import utils as h_utils
from . import settings
from .decorators import countries_safe_request
from .definitions import CountriesRunException
from . import models as countries_models
from . import errors as countries_errors
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
import os, time, random, datetime


random_string = "NeoCDRd09OWXXoecDVj9V3Ui0fit4uht"




def create_country(code, name, **kwargs):	
	country = h_utils.db_get_or_none(obj = countries_models.Country, code = code)
	if country:
		return country

	elif code not in [c[0] for c in countries_models.Country.code_choices]:
		raise CountriesRunError(code = -1, message = "country not supported")
	
	return h_utils.db_create(obj = countries_models.Country,
							 code = code,
							 name = name)


def get_country(**kwargs):
	return h_utils.db_get(obj = countries_models.Country, **kwargs)

def get_or_none_country(**kwargs):
	return h_utils.db_get_or_none(obj = countries_models.Country, **kwargs)

def filter_country(**kwargs):
	return h_utils.db_filter(obj = countries_models.Country, **kwargs)

def get_countries(**kwargs):
	return filter_country(**kwargs)

def create_region(country, code, name, **kwargs):
	kwargs["country"] = country
	kwargs["code"] = code.strip()
	kwargs["name"] = name.strip()
	return h_utils.db_create(countries_models.Region, **kwargs)


def get_region(**kwargs):
	return h_utils.db_get(obj = countries_models.Region, **kwargs)

def get_or_none_region(**kwargs):
	return h_utils.db_get_or_none(obj = countries_models.Region, **kwargs)	

def filter_region(**kwargs):
	return h_utils.db_filter(obj = countries_models.Region, **kwargs)

def create_province(region, code, name, **kwargs):
	kwargs["region"] = region
	kwargs["code"] = code.strip()
	kwargs["name"] = name.strip()
	return h_utils.db_create(countries_models.Province, **kwargs)


def get_province(**kwargs):
	return h_utils.db_get(obj = countries_models.Province, **kwargs)

def get_or_none_province(**kwargs):
	return h_utils.db_get_or_none(obj = countries_models.Province, **kwargs)	

def filter_province(**kwargs):
	return h_utils.db_filter(obj = countries_models.Province, **kwargs)

def create_commune(province, code, name, **kwargs):
	kwargs["province"] = province
	kwargs["code"] = code.strip()
	kwargs["name"] = name.strip()
	return h_utils.db_create(countries_models.Commune, **kwargs)

def get_or_none_commune(**kwargs):
	return h_utils.db_get_or_none(obj = countries_models.Commune, **kwargs)

def get_commune(**kwargs):
	return h_utils.db_get(obj = countries_models.Commune, **kwargs)	

def filter_commune(**kwargs):
	return h_utils.db_filter(obj = countries_models.Commune, **kwargs)


def create_useraddress(user, street, number, **kwargs):
	kwargs["user"] = user
	kwargs["street"] = street.strip()
	kwargs["number"] = number.strip()
	return h_utils.db_create(countries_models.UserAddress, **kwargs)

def get_or_none_useraddress(**kwargs):
	return h_utils.db_get_or_none(obj = countries_models.UserAddress, **kwargs)

def get_useraddress(**kwargs):
	return h_utils.db_get(obj = countries_models.UserAddress, **kwargs)	

def filter_useraddress(**kwargs):
	return h_utils.db_filter(obj = countries_models.UserAddress, **kwargs)
	