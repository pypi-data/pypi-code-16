from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils import timezone, timesince
from django.template.response import SimpleTemplateResponse
from . import settings
from . import definitions as handlers_definitions
from . import errors as handlers_errors
from . import models as handlers_models
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser

if settings.ENCRYPTION_ENABLED:
	from Crypto.PublicKey import RSA
	from Crypto.Cipher import XOR

if settings.PILL_ENABLED:
	from PIL import Image

from unidecode import unidecode
from htmlmin.minify import html_minify
import html.parser as HTLMParser
import time, random, datetime, os, string, re, requests, sys
import hashlib, sqlite3, ipaddress, tempfile, base64, mimetypes, urllib.request


if settings.DETECT_DEVICE:
	from user_agents import parse as device_parse


if settings.DETECT_COUNTRY:
	from django.contrib.gis.geoip2 import GeoIP2

if settings.CREATE_QR_CODES:
	import qrcode	

if settings.CREATE_BARCODES:
	import barcode


def safe_run(function_to_run, on_exception_return, *args, **kwargs):
	try:
		return function_to_run(*args, **kwargs)
	except Exception as e:
		return on_exception_return

def db_get(obj, **kwargs):
	return obj.objects.get( **kwargs )

def db_get_or_none(obj, **kwargs):
	try:
		return db_get(obj, **kwargs )
	except ObjectDoesNotExist:
		return None	

def db_create(obj, **kwargs):
	return obj.objects.create( **kwargs )

def db_get_or_create(obj, **kwargs):
	return obj.objects.get_or_create( **kwargs )

def db_delete(entry, **kwargs):
	return entry.delete()

def db_update(entry, **kwargs):
	for param, value in kwargs.items():
		setattr(entry, param, value)
	setattr(entry, "last_update", timezone.now())	
	entry.save()	
	return entry

def db_filter(obj, **kwargs):
	return obj.objects.filter( **kwargs )

def db_q(obj, q):
	return obj.objects.filter(q)

def db_unique_random(obj, initial_length = 10, max_length = 32, attribute = "identity", post_prefix = "", post_suffix = ""):
	string = get_random_string(max_length)
	for up_to in range(initial_length, max_length + 1):
		tmp_string = string[:up_to]
		if db_get_or_none(obj, **{attribute: tmp_string}):
			continue
		return post_prefix + tmp_string + post_suffix
	raise handlers_definitions.HandlersRunException(**handlers_errors.NO_UNIQUE_RANDOM_FOUND)

def db_unique_string(pattern, db_obj, initial_length = 20, attribute = "identity", to_int = False, post_prefix = "", post_suffix = ""):
	
	if to_int == True:
		string = '{}'.format(int( hashlib.sha256( pattern.encode('utf-8') ).hexdigest(), 16))
	else:
		string = hashlib.sha256( pattern.encode('utf-8') ).hexdigest()
	
	max_length = len(string)
	for up_to in range(initial_length, max_length + 1):

		tmp_string = string[:up_to]

		try:
			obj = db_obj.objects.get( **{ attribute: tmp_string } )
		except ObjectDoesNotExist:
			obj = None
		except Exception as e:
			raise handlers_definitions.HandlersRunException(**handlers_errors.QUERY_SET)
		
		if obj == None:
			string = tmp_string
			break
	else:
		raise handlers_definitions.HandlersRunException(**handlers_errors.NO_UNIQUE_STRING_FOUND)

	return post_prefix + string + post_suffix

def db_unique_string_hashed(*args, **kwargs):
	return db_unique_string(*args, **kwargs)	

def generic_unique_string(db_obj, initial_length = 20, pattern = None, attribute = "identity"):
	if pattern == None:
		pattern = "{}{}{}".format(get_random_string(5), time.time(), get_random_string(5))
	return db_unique_string(pattern = pattern,
							initial_length = initial_length,
							db_obj = db_obj,
							attribute = attribute)

def db_generic_unique_string(*args, **kwargs):
	return generic_unique_string(*args, **kwargs)

def db_unique_random_number(obj, initial_length = 10, max_length = 32, attribute = "identity", post_prefix = "", post_suffix = ""):
	string = get_random_string_number(max_length)
	for up_to in range(initial_length, max_length + 1):
		tmp_string = string[:up_to]
		if db_get_or_none(obj, **{attribute: tmp_string}):
			continue
		return post_prefix + tmp_string + post_suffix
	else:
		raise definitions.HandlersRunError(**HandlersErrors.NO_UNIQUE_RANDOM_FOUND)		

def get_random_string(length = 5):
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))
	
def random_string(length = 10):
	return get_random_string(length)

def get_random_string_number(length = 10):
	return ''.join(random.choice(string.digits) for x in range(length))

def random_string_number(length = 10):
	return get_random_string_number(length)

def random_string_hexdigits(length = 10):
	return ''.join(random.choice(string.hexdigits) for x in range(length))

def to_unicode(string, replace_empty = True, by_ch = "_"):
	text = unidecode(string)
	if replace_empty:
		text = text.replace(" ", by_ch)
		
	return text

def get_context(request):
	context = handlers_definitions.MiddlewareContext()

	context.debug = settings.DEBUG
	context.current_path = request.get_full_path()
	context.current_language = request.LANGUAGE_CODE
	context.now = timezone.now()
	context.address = request.META.get("REMOTE_ADDR", None)
	context.media_root = settings.MEDIA_ROOT
	context.host = settings.HOST
	context.subdomains = settings.SUBDOMAINS
	context.protocol = settings.PROTOCOL
	context.hostname = settings.HOSTNAME
	context.website_url = settings.WEBSITE_URL

	if settings.DETECT_DEVICE:
		context.device = get_device(request)
	else:
		context.device = None

	
	if settings.DETECT_COUNTRY:
		context.country = safe_run(geoip_country, None, context.address)
	else:
		context.country = None

	
	if settings.DETECT_LATITUDE_AND_LONGITUDE:
		context.lat_lon = safe_run(geoip_lat_lon, None, context.address)
	else:
		context.lat_lon = None


	return context	

def update_statistics(request, response):
	context = getattr(request, "context", {})
	c_handlers = context.get("c_handlers")
	
	if c_handlers is None:
		return

	delta_request = timezone.now() - c_handlers.now
	miliseconds = delta_request.microseconds / 1000


	old_total_requests = settings.STATATISTICS["total_requests"]
	total_requests = old_total_requests + 1
	if total_requests >= sys.maxsize:
		total_requests = 1
		settings.STATATISTICS["average_request_time"] = 0

		
	old_average_request_time = settings.STATATISTICS["average_request_time"]
	average_request_time = int( (old_average_request_time * old_total_requests + miliseconds) / total_requests )

	
	settings.STATATISTICS["total_requests"] = total_requests
	settings.STATATISTICS["average_request_time"] = average_request_time
	


	if settings.SAVE_STATISTICS and (total_requests % settings.SAVE_STATISTICS_EVERY_THIS_REQUESTS == 0):
		return db_create(handlers_models.Statistics,
			             total_requests = total_requests,
						 average_request_time = average_request_time)
		


def get_device(request):
	ua = device_parse(request.META.get("HTTP_USER_AGENT", ""))
	if ua.is_mobile:
		if ua.os.family == settings.DEVICE_IOS_NAME:
			return handlers_definitions.Device(is_ios = True, is_mobile = True)
		
		elif ua.os.family == settings.DEVICE_ANDROID_NAME:
			return handlers_definitions.Device(is_android = True, is_mobile = True)
		
		return handlers_definitions.Device(is_mobile = True)
	
	elif ua.is_pc:
		return handlers_definitions.Device(is_pc = True)
	
	elif ua.is_bot:
		return handlers_definitions.Device(is_bot = True)

	return None


def geoip(address):
	return GeoIP2(settings.GEOIP_PATH)

def geoip_country(address):
	return GeoIP2(settings.GEOIP_PATH).country(address)

def geoip_city(address):
	return GeoIP2(settings.GEOIP_PATH).city(address)

def geoip_lat_lon(address):
	return GeoIP2(settings.GEOIP_PATH).lat_lon(address)

def geoip_lon_lat(address):
	return GeoIP2(settings.GEOIP_PATH).lon_lat(address)

def geoip_geos(address):
	return GeoIP2(settings.GEOIP_PATH).geos(address)

def geoip_coords(address):
	return GeoIP2(settings.GEOIP_PATH).coords(address)

def send_html_email(to_email, from_email, subject, html):
	h = handlers_definitions.MailgunHandler(to_email = to_email,
											from_email = from_email,
										    subject = subject,
										    html = html,
										    domain = settings.MAILGUN_DOMAIN,
										    key = settings.MAILGUN_API_KEY)

	return h.send_html(html)


def create_landingmessage(name, subject, message, ip_address, **kwargs):
	kwargs["name"] = name.strip()
	kwargs["subject"] = subject.strip()
	kwargs["message"] = message.strip()
	kwargs["ip_address"] = ip_address.strip()
	return db_create(handlers_models.LandingMessage, **kwargs)

def create_landingemail(email, ip_address, **kwargs):
	kwargs["email"] = email.strip()
	kwargs["ip_address"] = ip_address.strip()
	return db_create(handlers_models.LandingEmail, **kwargs)

def is_string(string, min_length = 0):

	if type(string) != str:
		return False
		
	string = string.strip()	
	if not len(string) >= min_length:
		return False	
	return True	

def is_email_valid(email):
	regex = r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
	if re.match(regex, email) == None:
		return False
	return True
		
def is_content_harmful(string):
	return False

def is_url_safe(url):
	if not len(url) > 0:
		return False	
	return True

def is_file_safe(file_name):
	if not len(file_name) > 0:
		return False
	return True


file_safe_list = [ InMemoryUploadedFile, TemporaryUploadedFile]
def is_upload_file_safe(u_file):
	if not type(u_file) in file_safe_list:
		return False
	
	elif not len(u_file._name) > 0:
		return False
	
	elif not len(u_file.content_type) > 0:
		return False

	else:
		return True


def is_password_safe(password, **kwargs):		
	if not len(password) >= kwargs.get('length', 1):
		return False

	elif kwargs.get('lowercase', False) == True and re.search(r"[a-z]", password) == None:
		return False

	elif kwargs.get('uppercase', False) == True and re.search(r"[A-Z]", password) == None:
		return False

	elif kwargs.get('digits', False) == True and re.search(r"[0-9]", password) == None:
		return False

	return True	


def is_ip_address(ip):

	try:
		ipaddress.IPv4Address(ip)
	except Exception as e:
		pass
	else:
		return True

	try:
		ipaddress.IPv6Address(ip)
	except Exception as e:
		pass
	else:
		return True
	
	return False


def is_request(request):
	
	if hasattr(request, 'user') == False:
		return False

	elif hasattr(request, 'META') == False:
		return False

	elif hasattr(request, 'GET') == False:
		return False

	elif hasattr(request, 'POST') == False:
		return False	

	elif callable(getattr(request.user, 'is_authenticated')) == False:
		return False

	return True


def is_mix_type(var, types):
	o_type = type(var)
	for t in types:
		if o_type == t:
			return True
	return False

number_list = [int, float]
def is_number(num):
	if type(num) in number_list:
		return True
	return False


def is_valid_device(device):
	if device in settings.SUPPORTED_DEVICES:
		return True
	return False
	

def mix_cleaned_data(params, vars):
	t_params = {}			
	for var in vars:

		if var[0] == 'db':

			if var[2] == type(params[var[1]]):
				t_params[var[1]] = params[var[1]]
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_DB_TYPE)

		elif var[0] == 'string':

			if is_string(params[var[1]], var[2]):
				t_params[var[1]] = params[var[1]].strip()
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_STRING)

		elif var[0] == 'email':

			if is_email_valid(email = params[var[1]]):
				t_params[var[1]] = params[var[1]].strip()
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_EMAIL)

		elif var[0] == 'password':
			
			if is_password_safe(params[var[1]], **var[2]) == True:
				t_params[var[1]] = params[var[1]].strip()
			else:				
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_PASSWORD)

		elif var[0] == 'bool':

			for_true = var[2]['True']
			for_false = var[2]['False']

			if params[var[1]] == for_true:
				t_params[var[1]] = True
			elif params[var[1]] == for_false:
				t_params[var[1]] = False
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_BOOL)
		
		elif var[0] == 'type':

			if type(params[var[1]]) == var[2]:
				t_params[var[1]] = params[var[1]]
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.WRONG_TYPE)

		elif var[0] == 'url':

			if is_url_safe(url = params[var[1]]) == True:
				t_params[var[1]] = params[var[1]]
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_URL)
		
		elif var[0] == 'file':

			if is_file_safe(file_name = params[var[1]]) == True:
				t_params[var[1]] = params[var[1]].strip()
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_FILE)

		elif var[0] == 'u_file':
			
			if is_upload_file_safe(u_file = params[var[1]]) == True:
				t_params[var[1]] = params[var[1]]
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_UPLOAD_FILE)

		elif var[0] == 'ip':
			
			if is_ip_address(ip = params[var[1]]) == True:				
				t_params[var[1]] = params[var[1]]			
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_IP_ADDRESS)

		elif var[0] == 'request':
			
			if is_request(request = params[var[1]]) == True:
				t_params[var[1]] = params[var[1]]			
			else:				
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_REQUEST)
		
		elif var[0] == 'c_request':
			
			if is_custom_request(request = params[var[1]], to_check = var[2]) == True:
				t_params[var[1]] = params[var[1]]			
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_CUSTOM_REQUEST)

		elif var[0] == 'username':
			
			if var[2] == 'email':

				if is_email_valid(email = params[var[1]]) == True:

					t_params[var[1]] = params[var[1]].strip()
				else:

					raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_USERNAME)

			elif var[2] == 'string':

				t_params[var[1]] = params[var[1]].strip()[:settings.MAX_USERNAME_LENGTH]
										
			else:

				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_USERNAME)
				
		elif var[0] == 'mix':

			if is_mix_type(var = params[var[1]],types = var[2]) == True:
				t_params[var[1]] = params[var[1]]

			else:

				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_MIX_TYPE)
		
		elif var[0] == 'regex':

			if re.match(var[2], var[1]):
				t_params[var[1]] = params[var[1]]
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_REGEX)

		elif var[0] == 'number':

			if is_number(params[var[1]]):
				t_params[var[1]] = params[var[1]]
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_NUMBER)

		
		elif var[0] == 'device':

			if is_valid_device(params[var[1]]):
				t_params[var[1]] = params[var[1]]
			else:
				raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_DEVICE)

		else:

			raise handlers_definitions.HandlersRunException(**handlers_errors.INVALID_TYPE)
				
	return t_params	

def cleaned(params, vars):
	return mix_cleaned_data(params, vars)


def create_dictionary(**kwargs):
	dictionary = {}
	for k, v in kwargs.items():	
		dictionary[k] = v
	else:
		return dictionary

def dict(**kwargs):
	return create_dictionary(**kwargs)

def join_dictionaries(*args):
	joined_dictionary = {}
	for dict_value in args:	
			
		for k, v in dict_value.items():
			joined_dictionary[k] = v

	else:
		return joined_dictionary

def join_dicts(*args):
	return join_dictionaries(*args)


def is_older_than_now(date, **kwargs):
	if timezone.now() > date + relativedelta( **kwargs ):
		return True
	return False

def generate_RSA(bits = 2048, rand = os.urandom):
	key = RSA.generate(bits,  rand, e = 65537) 
	public_key = key.publickey().exportKey("PEM")
	private_key = key.exportKey("PEM") 
	return private_key, public_key


def render_template(template, context, **kwargs):
	return SimpleTemplateResponse(template, context).render()

def template_response(template, context, **kwargs):
	rendered = render_template(template, context)
	content = rendered.content.replace(b'\n', b'')
	content = content.replace(b'\t', b'')

	html = HTLMParser.unescape( content.decode('utf-8') )
	if kwargs.get("minify"):
		return html_minify(html)
	return html


def create_qr(text, **kwargs):
	dst = tempfile.NamedTemporaryFile(suffix = '.png', delete = False)

	qr = qrcode.QRCode(
		version = kwargs.get("version", 1),
		error_correction = qrcode.constants.ERROR_CORRECT_L,
		box_size = kwargs.get("box_size", 10),
		border = kwargs.get("border", 4),
	)

	qr.add_data(text)
	qr.make(fit = kwargs.get("fit", True))
	img = qr.make_image()
	img.save(dst.name)

	return dst.name

def create_barcode(text, **kwargs):
	dst = tempfile.NamedTemporaryFile(delete = False)
	ean = barcode.get(kwargs.get('format','ean13'), text, writer = barcode.writer.ImageWriter())
	return ean.save(dst.name)

def guess_mimetype(filename):
	return mimetypes.guess_type(filename)[0]
	
def get_local_image(path, dst_suffix = ".jpg", dst_format = "JPEG", dst_quality = 95):

	with open(path, 'rb') as image:
		content = image.read()
	
	filename = path.rsplit("/", 1)[-1]
	name, extension = filename.rsplit(".", 1)
	f1 = tempfile.NamedTemporaryFile(suffix="." + extension, delete = False)
	f1.write(content)
	f1.close()

	im = Image.open(f1.name)
	f2 = tempfile.NamedTemporaryFile(suffix = dst_suffix)
	im.save(f2.name, format = dst_format, quality = dst_quality, optimize = True)


	mimetype = guess_mimetype(filename)
	if not mimetype:
		mimetype = "image/"
		
	tp = TemporaryUploadedFile(f2.name,
							   mimetype,
							   0,
							   None)
	
	tp.write(f2.read())
	return tp


def download_file(url, **kwargs):
	url_f = url.split("?", 1)[0]
	rest, filename = url_f.rsplit("/", 1)
	name, extension = filename.rsplit(".", 1)

	dst = tempfile.NamedTemporaryFile(suffix = '.' + extension, delete = False)
	urllib.request.urlretrieve(url, dst.name)
	return dst.name

def download_and_get_local_image(url, **kwargs):
	path = download_file(url)

	return get_local_image(path)


def create_contactmessage(subject, email, message, ip_address, **kwargs):
	kwargs["subject"] = subject
	kwargs["email"] = email.strip()
	kwargs["message"] = message.strip()
	kwargs["ip_address"] = ip_address.strip()

	return h_utils.db_create(handlers_models.ContactMessage, **kwargs)

def get_contactmessage(**kwargs):
	return h_utils.db_get(handlers_models.ContactMessage, **kwargs)

def filter_contactmessage(**kwargs):
	return h_utils.db_filter(handlers_models.ContactMessage, **kwargs)

def check_google_recaptcha(response, remoteip, **kwargs):
	data = {
		"secret" : settings.GOOGLE_RECAPTCHA_SECRET,
		"response" : response,
		"remoteip" : remoteip,
	}

	try:
		res = requests.post(settings.GOOGLE_RECAPTCHA_VERIFY_URL, data = data)
	except Exception as e:
		res = None
		
	if res == None or res.status_code != 200:
		raise handlers_definitions.HandlersRunException(**handlers_errors.ERROR_SENDING_REQUEST, extra = res.text)

	r = res.json()
	return r.get("success", False)




