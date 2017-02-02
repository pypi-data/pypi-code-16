from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers import utils as h_utils
from . import settings
from .decorators import currencies_safe_request
from .definitions import CurrenciesRunException
from . import models as currencies_models
from . import errors as currencies_errors
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
import os, time, random, datetime


random_string = "z6LYWH8sK7DdUtlP1aGcMNSg50BQpkd0"




def create_currency(code, name, symbol, decimals, **kwargs):	
	currency = h_utils.db_get_or_none(obj = currencies_models.Currency, code = code)
	if currency != None:
		return currency

	elif code not in [c[0] for c in currencies_models.Currency.code_choices]:
		raise CurrenciesRunError(code = -1, message = "currency not supported")
	
	return h_utils.db_create(obj = currencies_models.Currency,
							 code = code.strip(),
							 name = name.strip(),
							 symbol = symbol.strip(),
							 decimals = decimals)


def create_convertionrate(input, output, source, rate, **kwargs):
	convertion_rate = h_utils.db_create(obj = currencies_models.ConvertionRate,
										input = input,
									    output = output,
									    source = source,
									    rate = rate)


	last = h_utils.db_get_or_none(obj = currencies_models.LastConvertionRate,
								  convertion_rate__input = input,
								  convertion_rate__output = output)

	if last == None:
		last = h_utils.db_create(obj = currencies_models.LastConvertionRate,
								 convertion_rate = convertion_rate)
		return convertion_rate

	else:

		last = h_utils.db_update(entry = last,
								 convertion_rate = convertion_rate)

		return convertion_rate




def exchange(amount, input, output, **kwargs):
	rate = get_exchange_rate_value(input = input,
								   output = output)

	if kwargs.get("formated", True):
		return round(amount * rate, output.decimals)
	return amount * rate


def get_exchange_rate_value(input, output, **kwargs):
	last = h_utils.db_get_or_none(obj = currencies_models.LastConvertionRate,
								  convertion_rate__input = input,
								  convertion_rate__output = output)

	if last != None:
		return last.convertion_rate.rate
	
	last = h_utils.db_get_or_none(obj = currencies_models.LastConvertionRate,
								  convertion_rate__input = output,
								  convertion_rate__output = input)

	if last != None and last.convertion_rate.rate > 0:
		return 1.0 / last.convertion_rate.rate
	
	raise CurrenciesRunException( **currencies_errors.NO_LAST_CONVERTION_RATE )


def get_currency(*args, **kwargs):
	return h_utils.db_get(obj = currencies_models.Currency, **kwargs)

def get_currencies(*args, **kwargs):
	return h_utils.db_filter(obj = currencies_models.Currency, **kwargs)

def get_convertionrate(*args, **kwargs):
	return h_utils.db_get(obj = currencies_models.ConvertionRate, **kwargs)

def get_convertionrates(*args, **kwargs):
	return h_utils.db_filter(obj = currencies_models.ConvertionRate, **kwargs)	

def get_lastconvertionrate(*args, **kwargs):
	return h_utils.db_get(obj = currencies_models.LastConvertionRate, **kwargs)

def get_lastconvertionrates(*args, **kwargs):
	return h_utils.db_filter(obj = currencies_models.LastConvertionRate, **kwargs)