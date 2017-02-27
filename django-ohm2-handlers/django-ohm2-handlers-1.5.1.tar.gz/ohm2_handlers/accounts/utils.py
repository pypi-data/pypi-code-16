from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password, password_changed, password_validators_help_texts
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.db.models import Q
from rest_framework.authtoken.models import Token
from ohm2_handlers import utils as h_utils
from ohm2_handlers.currencies import utils as currencies_utils
from ohm2_handlers.countries import utils as countries_utils
from . import settings
from . import models as accounts_models
from . import errors as accounts_errors
from .decorators import accounts_safe_request
from .definitions import AccountsRunException
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
from Crypto.Cipher import AES
from Crypto import Random
import os, time, random, datetime, base64, importlib


random_string = "ufP9sqTiVW2dQDqrmPCwOcAr79xauXpV"




def get_context(request):
	if request.user.is_authenticated:
		user = get_user(username = request.user.get_username())
	else:
		user = None	
	
	context = {
		"user" : user,
	}
	return context

def change_password(user, password):
	user.set_password(password)
	user.save()
	return user

def user_authenticate(username, password):
	return authenticate(username = username, password = password)

def user_login(request, auth_user):
	return login(request, auth_user)

def user_logout(request):
	return logout(request)

def check_user_integrity(user, **kwargs):
	settings = get_or_none_settings(user = user)
	if settings is None:
		settings = create_settings(user, **kwargs.get("settings", {}))

	keys = get_or_none_keys(user = user)
	if keys is None:
		keys = create_keys(user)
	
	avatars = get_or_none_avatars(user = user)
	if avatars is None:
		avatars = create_avatars(user, **kwargs.get("avatars", {}))
	
	referalcodes = get_referalcodes(user = user)
	if len(referalcodes) == 0:
		referalcode = create_referalcode(user)
	
	authtoken = get_or_create_authtoken(user)

	crypto = get_or_none_crypto(user = user)
	if crypto is None:		
		crypto = create_crypto(user)


	return h_utils.db_update(user)	

def check_users_integrity(**kwargs):
	users = h_utils.db_filter(User)
	
	if kwargs.get("show_progress", False):

		u_len = len(users)
		count = 0
		for user in users:
			user = check_user_integrity(user)
			count += 1
			print("[{2}] User: {0} ; Progress: {1}".format(user.get_username(), round(count / u_len * 100, 2), count))

	else:
		
		for user in users:
			user = check_user_integrity(user)

	return True	

def create_user(username, email, password, **kwargs):

	if settings.UNIQUE_USER_EMAILS:
		if filter_user(email = email).count() > 0:
			raise AccountsRunException(**accounts_errors.EMAIL_ALREADY_REGISTERED)

	user = User.objects.create_user(username = username,
								    email = email,
								    password = password)
	

	return user


def get_user(**kwargs):
	return h_utils.db_get(User, **kwargs)

def get_user_or_none(**kwargs):
	try:
		return get_user(**kwargs)
	except ObjectDoesNotExist:
		return None

def get_or_none_user(**kwargs):
	return get_user_or_none(**kwargs)	

def get_users(**kwargs):
	return h_utils.db_filter(obj = User, **kwargs)

def filter_user(**kwargs):
	return h_utils.db_filter(obj = User, **kwargs)

def user_exist(**kwargs):
	if filter_user(**kwargs).count() > 0:
		return True
	return False

def create_superuser(username, email, password, **kwargs):
	user = create_user(username, email, password)

	return h_utils.db_update(user, is_staff = True, is_superuser = True)
		

def create_settings(user, **kwargs):
	country = kwargs.get("country", None)
	if not country:
		country = countries_utils.get_country(code = settings.DEFAULT_COUNTRY)

	currency = kwargs.get("currency", None)
	if not currency:
		currency = currencies_utils.get_currency(code = settings.DEFAULT_CURRENCY)

	timezone = kwargs.get("timezone", None)
	if not timezone or not timezone in settings.TIMEZONES:
		timezone = settings.DEFAULT_TZ

	language = kwargs.get("language", get_language())
	if not language or not language in [lang[0] for lang in settings.LANGUAGES]:
		language = settings.LANGUAGE_CODE	

	change_password = kwargs.get("change_password", False)
	email_validated = kwargs.get("email_validated", False)

	return h_utils.db_create(accounts_models.Settings,
							 user = user,
							 country = country,
							 currency = currency,
							 timezone = timezone,
							 language = language,
							 change_password = change_password,
							 email_validated = email_validated)

def get_settings(**kwargs):
	return h_utils.db_get(accounts_models.Settings, **kwargs)

def get_or_none_settings(**kwargs):
	try:
		return get_settings(**kwargs)
	except ObjectDoesNotExist:
		return None	

def filter_settings(**kwargs):
	return h_utils.db_filter(accounts_models.Settings, **kwargs)

def update_settings(settings, **kwargs):
	return h_utils.db_update(settings, **kwargs)
	
def create_keys(user):
	private_1024, public_1024 = h_utils.generate_RSA(bits = 1024)
	private_2048, public_2048 = h_utils.generate_RSA(bits = 2048)
	return h_utils.db_create(accounts_models.Keys,
							 user = user,
							 private_1024 = private_1024,
							 public_1024 = public_1024,
							 private_2048 = private_2048,
							 public_2048 = public_2048)

def get_keys(**kwargs):
	return h_utils.db_get(accounts_models.Keys, **kwargs)

def get_or_none_keys(**kwargs):
	try:
		return get_keys(**kwargs)
	except ObjectDoesNotExist:
		return None	

def filter_keys(**kwargs):
	return h_utils.db_filter(accounts_models.Keys, **kwargs)	

def create_avatars(user, **kwargs):
	kwargs["identity"] = h_utils.db_unique_random_number(accounts_models.Avatars)
	kwargs["user"] = user

	original = kwargs.get("original", None)
	if original:
		kwargs["original"] = process_avatars_original(original)

	return h_utils.db_create(accounts_models.Avatars, **kwargs)


def process_avatars_original(original):
	return original

def get_avatars(**kwargs):
	return h_utils.db_get(accounts_models.Avatars, **kwargs)

def get_or_none_avatars(**kwargs):
	try:
		return get_avatars(**kwargs)
	except ObjectDoesNotExist:
		return None

def filter_avatars(**kwargs):
	return h_utils.db_filter(accounts_models.Avatars, **kwargs)	

def validate_current_password(password, user = None, password_validators = None):
	try:
		validate_password(password, user, password_validators)
	except ValidationError as e:
		return [reason for reason in e]
	return []

def is_password_secure(password, user = None, password_validators = None):
	errors = validate_current_password(password, user, password_validators)
	if len(errors) == 0:
		return True
	return False

def get_passwordreset(**kwargs):
	return h_utils.db_get(accounts_models.PasswordReset, **kwargs)

def get_passwordreset_or_none(**kwargs):
	try:
		return get_passwordreset(**kwargs)
	except ObjectDoesNotExist:
		return None

def get_or_none_passwordreset(**kwargs):
	return get_passwordreset_or_none(**kwargs)

def get_or_create_passwordreset(user, request):
	reset = h_utils.db_get_or_none(obj = accounts_models.PasswordReset,
								   user = user,
								   activation_date = None)
	if reset:
		if reset.ip != request.META["REMOTE_ADDR"]:
			reset = h_utils.db_update(reset, ip = request.META["REMOTE_ADDR"])
		return reset

	code = h_utils.db_unique_random_number(accounts_models.PasswordReset, initial_length = 6, attribute="code")	
	return h_utils.db_create(accounts_models.PasswordReset,
							 identity = h_utils.db_unique_random(accounts_models.PasswordReset, 32),
							 user = user,
							 ip = request.META["REMOTE_ADDR"],
							 code = code)


def send_passwordreset(reset, request, **kwargs):
	request.context["ret"] = {
		'reset' :reset,
		'website_url' : settings.WEBSITE_URL,
	}

	html = h_utils.template_response(settings.PASSWORD_RESET_TEMPLATE_PATH, request.context)
	ret = h_utils.send_html_email(to_email = reset.user.email,
							      from_email = settings.PASSWORD_RESET_FROM_EMAIL,
							      subject = _(settings.PASSWORD_RESET_SUBJECT),
							      html = html)
	
	if ret:
		return h_utils.db_update(reset,
								 last_sent_date = timezone.now())
	return reset


def create_referalcode(user, **kwargs):
	code = h_utils.db_unique_random_number(accounts_models.ReferalCode,
										   attribute = "code",
										   initial_length = settings.REFERAL_CODE_LENGTH)
	
	return h_utils.db_create(accounts_models.ReferalCode,
							 user = user,
							 code = code)

def get_referalcode(**kwargs):
	return h_utils.db_get(accounts_models.ReferalCode, **kwargs)	

def get_or_none_referalcode(**kwargs):
	try:
		return get_referalcode(**kwargs)
	except ObjectDoesNotExist:
		return None

def get_referalcodes(**kwargs):
	return h_utils.db_filter(accounts_models.ReferalCode, **kwargs)

def get_authtoken(user):
	return h_utils.db_get(Token, user = user)

def get_or_none_authtoken(user):
	try:
		return get_authtoken(user)
	except ObjectDoesNotExist:
		return None

def get_or_create_authtoken(user):
	token, created = Token.objects.get_or_create(user = user)
	return token

def update_avatars(avatars, **kwargs):
	
	original = kwargs.get("original", None)
	if original:
		kwargs["original"] = process_avatars_original(original)
	
	return h_utils.db_update(avatars, **kwargs)

def get_timezones():
	return settings.TIMEZONES

def get_timezones_dict():
	timezones = []
	for tz in get_timezones():
		name = tz.replace("_", " ")
		d = h_utils.dict(tz = tz, name = _(name))
		timezones.append(d)
	return timezones	

def get_languages():
	return settings.LANGUAGES

def get_languages_dict():
	languages = []
	for lang in get_languages():
		d = h_utils.dict(code = lang[0], name = _(lang[1]))
		languages.append(d)
	return languages

def activate_language(request, lang):
	if lang in [la[0] for la in get_languages()]:
		translation.activate(lang)
		request.session[translation.LANGUAGE_SESSION_KEY] = lang
		return True
	return False	

def change_password_with_passwordreset(passwordreset, password):
	user = change_password(passwordreset.user, password)
	return h_utils.db_update(passwordreset, activation_date = timezone.now())

def create_crypto(user, **kwargs):
	kwargs["user"] = user
	kwargs["key_16"] = h_utils.random_string(16)
	kwargs["mode_16"] = AES.MODE_CFB
	kwargs["iv_16"] = base64.b64encode(Random.new().read(AES.block_size))
	return h_utils.db_create(accounts_models.Crypto, **kwargs)

def get_crypto(**kwargs):
	return h_utils.db_get(accounts_models.Crypto, **kwargs)

def get_or_none_crypto(**kwargs):
	try:
		return get_crypto(**kwargs)
	except ObjectDoesNotExist:
		return None

def update_user(user, **kwargs):
	return h_utils.db_update(user, **kwargs)

def create_presignup(email, **kwargs):
	kwargs["email"] = email
	return h_utils.db_create(accounts_models.Presignup, **kwargs)

def get_presignup(**kwargs):
	return h_utils.db_get(accounts_models.Presignup, **kwargs)

def get_or_none_presignup(**kwargs):
	return h_utils.db_get_or_none(accounts_models.Presignup, **kwargs)		

def send_presignup(presignup, request, **kwargs):
	request.context["ret"] = {
		'presignup' :presignup,
		'website_url' : settings.WEBSITE_URL,
		'extras' : kwargs.get("extras", None),
	}

	device = kwargs.get("device")
	if device:
		c_handlers = request.context["c_handlers"]
		c_handlers["device"] = device
		request.context["c_handlers"] = c_handlers


		
	template_path = kwargs.get("template_path", settings.PRESIGNUP_TEMPLATE_PATH)
	html = h_utils.template_response(template_path, request.context)

	ret = h_utils.send_html_email(to_email = presignup.email,
							      from_email = settings.PRESIGNUP_FROM_EMAIL,
							      subject = _(settings.PRESIGNUP_SUBJECT),
							      html = html)
	
	if ret:
		return h_utils.db_update(presignup,
								 last_sent = timezone.now())
	return presignup


def activate_presignup(presignup, **kwargs):
	return h_utils.db_update(presignup, activation_date = timezone.now())


def create_alias(user, name, **kwargs):
	kwargs["user"] = user
	kwargs["name"] = name.strip()
	return h_utils.db_create(accounts_models.Alias, **kwargs)

def get_alias(**kwargs):
	return h_utils.db_get(accounts_models.Alias, **kwargs)	

def get_or_none_alias(**kwargs):
	try:
		return get_alias(**kwargs)
	except ObjectDoesNotExist:
		return None


def run_signup_pipeline(user, request, **kwargs):
	previous_outputs = {}
	for pipeline in settings.SIGNUP_PIPELINE:

		func = pipeline.rsplit(".", 1)[-1]
		
		m = importlib.import_module(pipeline)
		function = getattr(m, func)

		user, output = function(user, request, previous_outputs)

		previous_outputs = h_utils.join_dicts(previous_outputs, output)

	return user	



def run_logout_pipeline(request, **kwargs):
	previous_outputs = {}
	for pipeline in settings.LOGOUT_PIPELINE:

		func = pipeline.rsplit(".", 1)[-1]
		
		m = importlib.import_module(pipeline)
		function = getattr(m, func)

		output = function(request, previous_outputs)

		previous_outputs = h_utils.join_dicts(previous_outputs, output)

	return None


def run_login_pipeline(request, auth_user, **kwargs):
	previous_outputs = {}
	for pipeline in settings.LOGIN_PIPELINE:

		func = pipeline.rsplit(".", 1)[-1]
		
		m = importlib.import_module(pipeline)
		function = getattr(m, func)

		auth_user, output = function(request, auth_user, previous_outputs)

		previous_outputs = h_utils.join_dicts(previous_outputs, output)

	return None


