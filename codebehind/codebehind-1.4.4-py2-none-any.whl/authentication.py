import urllib, hashlib, hmac, re
import time
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from codebehind.models import UserSecret


class CodeBehindAuthentication(authentication.BaseAuthentication):
	"""
	This will check if the Signature of the client is valid.
	author: Michael Henry Pantaleon
			me@iamkel.net
	format: 
	Authorization: algorithm Credential=username SignedHeaders=SignedHeaders Signature=signature
	sample:
	# Authorization: X-HMAC-SHA256 Credential=USERNAME SignedHeaders=content-type;host;x-header Signature=CALCULATED_SIGNATURE
	"""

	def remove_prefix(self, text, prefix):
		return text[text.startswith(prefix) and len(prefix):]

	def get_request_headers(self, request):
		"""
		this will trim, and will get only the request header
		"""
		regex_http = re.compile(r'^(HTTP_.+|X_.+|CONTENT_TYPE|CONTENT_LENGTH)$')
		request_headers = {}
		for header in request.META:

			if regex_http.match(header):
				strip_header = self.remove_prefix(header, "HTTP_").replace("_","-").lower().strip()
				request_headers[strip_header] = self.trim_header_value(request.META[header])
		return request_headers

	def get_valid_headers(self, keys_of_valid_headers, headers):
		"""
		this get all headers from the authorizationHeader.signedHeader
		"""
		keys = keys_of_valid_headers.split(";")
		valid_headers = {}
		for key in keys:
			if headers.has_key(key):
				valid_headers[key] = headers[key]
		return valid_headers

	def sign(self, key, msg):
		"""
		this will do the hmac signing
		"""
		return hmac.new(key, msg, hashlib.sha256)

	def trim_header_value(self, text):
		text = re.sub(r" +", " ", text)
		return text.strip()

	def get_signature_key(self, key, timestamp):
		"""
		hmac of secretkey and timestamp
		can include other info also
		"""
		return self.sign(key, timestamp).digest()

	def sort_dict(self, dict):
		"""
		This will sort dictionary according to keys
		"""
		return sorted(dict.items())

	def url_encode(self, text):
		return urllib.quote(text)

	def get_canonical_param(self, dict):
		"""
		- sorted by key
		- convert value to string
		- separated by =
		- uri_encoded key
		- uri_encoded value
		
		url_encoded(key)=url_encoded(value)

		eg. age=20&name=kel&x-var=32
		"""
		try:
			if dict == None or len(dict) == 0:
				return ''
			return '&'.join("%s=%s" % (self.url_encode(key), self.url_encode(str(val))) for (key,val) in self.sort_dict(dict))
		except Exception, e:
			print e

	def get_canonical_headers(self, headers):
		"""
		- header name and value is separated by colon
		- reduced consecutive white spaces into single white space
		- trimmed leading and trailing in header name
		- append \n after every header value
		
		name:value\n

		eg. 
		content-type:application/json\n
		length:100\n

		"""
		return ''.join("%s:%s\n" % (key, str(val)) for (key,val) in self.sort_dict(headers))
		
	def get_signed_headers(self, headers):
		"""
		- only header name separate by semi colon.
		eg.
		content-type;length;
		"""
		return ';'.join("%s" % (key) for (key,val) in self.sort_dict(headers))

	def get_signature(self, 
		access_key, 
		secret_key, 
		algorithm, 
		http_method, 
		canonical_uri, 
		timestamp, 
		query_param={}, 
		headers={},
		payload={}):

		"""
		This will get the signature
		"""
		
		canonical_query_string = self.get_canonical_param(query_param)
		canonical_headers = self.get_canonical_headers(headers)
		signed_headers = self.get_signed_headers(headers)
		canonical_payload = self.get_canonical_param(payload)
		canonical_payload_hash = hashlib.sha256(canonical_payload).hexdigest()

		canonical_request = "%s\n%s\n%s\n%s\n%s\n%s" % (
			http_method, 
			canonical_uri,
		 	canonical_query_string, 
		 	canonical_headers, 
		 	signed_headers, 			 	
		 	canonical_payload_hash)

		canonical_request_hash = hashlib.sha256(canonical_request).hexdigest()

		string_to_sign = "%s\n%s\n%s" % (
			algorithm, 
			timestamp, 
			canonical_request_hash)

		signature_key = self.get_signature_key(secret_key, timestamp)
		signature = self.sign(signature_key, string_to_sign)
		signature_hex = signature.hexdigest()
		return signature_hex

	def get_auth_header(self,
		access_key,
		algorithm,
		signed_headers,
		signature):
		"""
		Formatting for the authorization header
		format:
		algorithm Credential=access key ID, SignedHeaders=SignedHeaders, Signature=signature
		"""
		return "%s Credential=%s SignedHeaders=%s Signature=%s" % (
			algorithm, 
			access_key, 
			signed_headers, 
			signature)

	def authenticate(self, request):

		"""
		this will handle the authentication of every request
		"""

		try:
			cb_config = {}

			if hasattr(settings, 'CODEBEHIND_CONFIG'):
				cb_config = settings.CODEBEHIND_CONFIG

			algorithm = cb_config.get("ALGORITHM", "X-HMAC-256")
			signing_query_prefix = cb_config.get("SIGNING_QUERY_PREFIX","X")
			validity_duration = cb_config.get("VALIDITY_DURATION", 15 * 60)

			request_algorithm = ""
			request_credential = ""
			request_timestamp = ""
			request_signed_headers = ""
			request_signature = ""
			request_qparams = request.query_params

			request_headers = self.get_request_headers(request)

			if not request_headers.get("authorization") == None:
				# if has authorization header then use this method
				request_auth_header = request_headers.get("authorization", "")
				auth_header_info = request_auth_header.split(" ")
				if not len(auth_header_info) == 4:
					return None
				
				request_algorithm = auth_header_info[0]
				request_credential = auth_header_info[1].split("=")[1]
				request_signed_headers = auth_header_info[2].split("=")[1]
				request_valid_headers = self.get_valid_headers(request_signed_headers, 
					request_headers)
				request_signature = auth_header_info[3].split("=")[1]
				request_timestamp = request_headers.get('x-timestamp')

			elif not request_qparams.get("%s-Algorithm" % signing_query_prefix) == None:
				# if signed using query parameters
				request_algorithm = request_qparams.get("%s-Algorithm" % signing_query_prefix)
				request_credential = request_qparams.get("%s-Credential" % signing_query_prefix)
				request_timestamp = request_qparams.get("%s-Timestamp" % signing_query_prefix)
				request_signed_headers = request_qparams.get("%s-SignedHeaders" % signing_query_prefix)
				request_valid_headers = self.get_valid_headers(request_signed_headers, 
					request_headers)
				request_signature = request_qparams.get("%s-Signature" % signing_query_prefix)
				regex_signing_qparams = re.compile(r'^(%s-.+)$' % signing_query_prefix)
				request_qparams = {key: value for key, value in request_qparams.items() if not regex_signing_qparams.match(key)}
				

			if not algorithm == request_algorithm:
				raise exceptions.AuthenticationFailed('Invalid algorithm.')

			request_payload = request.data

			canonical_uri = request.META.get('PATH_INFO')
			content_type = request.content_type
			request_method = request.method
			
			user = get_object_or_404(get_user_model(), username=request_credential)
			user_secret_key = user.secret

			server_time_unix = float(time.time())

			if abs(server_time_unix - float(request_timestamp)) > validity_duration:
				raise exceptions.AuthenticationFailed('Invalid request time.')

			access_key = user.username
	 
			signature = self.get_signature(
				access_key, 
				str(user.secret.key), 
				request_algorithm, 
				request_method, 
				canonical_uri,
				request_timestamp, 
				request_qparams,
				request_valid_headers,
				request_payload)
			
			if not signature == request_signature:
				raise exceptions.AuthenticationFailed('Signature don\'t matched.')
			
			return (user, None)

		except Exception, e:
			raise e
		
		

