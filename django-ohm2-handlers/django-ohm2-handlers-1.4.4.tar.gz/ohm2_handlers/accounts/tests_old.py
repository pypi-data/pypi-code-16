from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.management import call_command
from ohm2_handlers import utils as h_utils
from ohm2_handlers import settings as h_settings
from ohm2_handlers.currencies import utils as currencies_utils
from ohm2_handlers.countries import utils as countries_utils
from ohm2_handlers.accounts import utils as accounts_utils
from ohm2_handlers.accounts import serializers as accounts_serializers
from ohm2_handlers.accounts import settings
from ohm2_handlers.accounts import errors as accounts_errors
import simplejson as json



class UsersTestCase(TestCase):
	
	test_username = "testusername"
	test_email = "slipktonesraton@gmail.com"
	test_password = h_utils.random_string(10)

	def test_encrypt_message(self):
		
		user = accounts_utils.create_user(self.test_username, self.test_email, self.test_password, last_name = "Lastname ", first_name = "Firstname")
		self.assertEqual(user.get_username(), self.test_username)

		for length in range(1, 1024):
			
			message = h_utils.random_string(length)
			cipher = user.crypto.encrypt_16(message)
			message_2 = user.crypto.decrypt_16(cipher)
			self.assertEqual(message, message_2.decode("utf-8"))
		

	def test_user_serializer(self):

		username = "asdasd"
		email = "asd@asd.com"
		password = "asd"

		user = accounts_utils.create_user(username, email, password, last_name = "Lastname ", first_name = "Firstname")
		self.assertEqual(user.get_username(), username)

		ser = accounts_serializers.User(user)
		

	def test_create_user(self):

		username = "asd"
		email = "asd@asd.com"
		password = "asd"

		user = accounts_utils.create_user(username, email, password)

		self.assertEqual(user.get_username(), username)

	def setUp(self):
		countries_utils.create_country(code = "CL", name = "Chile")
		currencies_utils.create_currency(code = "CLP",
										 name = "Chiean peso",
										 symbol = '$',
										 decimals = 0)
										 	
class ApiTestCase(TestCase):
	
	test_username = "testusername"
	test_email = "slipktonesraton@gmail.com"
	test_password = h_utils.random_string(10)
	test_alias = "testalias"

	test_long_email = h_utils.random_string(30) + "@fakedomain.com"
	test_long_email_password = h_utils.random_string(10)

	test_email_2 = "oliverherreram@gmail.com"


	def test_login_by_alias_success(self):
		SIGNUPS_ENABLED_ORIGINAL = settings.SIGNUPS_ENABLED
		settings.SIGNUPS_ENABLED = True

		ENABLE_ALIAS_LOGIN_ORIGINAL = settings.ENABLE_ALIAS_LOGIN
		settings.ENABLE_ALIAS_LOGIN = True
		
		SIGNUP_USERNAME_TRUNCATION_ORIGINAL = settings.SIGNUP_USERNAME_TRUNCATION
		settings.SIGNUP_USERNAME_TRUNCATION = True

		LOGIN_USERNAME_TRUNCATION_ORIGINAL = settings.LOGIN_USERNAME_TRUNCATION
		settings.LOGIN_USERNAME_TRUNCATION = True


		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_alias,
			"password" : self.test_password,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)

		settings.SIGNUPS_ENABLED = SIGNUPS_ENABLED_ORIGINAL
		settings.ENABLE_ALIAS_LOGIN = ENABLE_ALIAS_LOGIN_ORIGINAL
		settings.SIGNUP_USERNAME_TRUNCATION = SIGNUP_USERNAME_TRUNCATION_ORIGINAL
		settings.LOGIN_USERNAME_TRUNCATION = LOGIN_USERNAME_TRUNCATION_ORIGINAL


	def test_avatars_serializer(self):
		user = accounts_utils.get_user(username = self.test_username)
		avatars = accounts_utils.get_avatars(user = user)
		
		zer = accounts_serializers.Avatars(avatars)

		

	def test_facebook_signup(self):
		access_token = "EAACEdEose0cBAPXKqqNNtnIZBQ3GHiJOFmqyfU8J8YGl4X9xfxfKjlv51Wp5I6pnxqZAoQSbZBHh423DjzJS5nO6UCzCK6c5jfE2Jv8Ao8w4EKeM7Iv5XnJnJRZC3YC1zzu7ijNMFkc5W6n1dVyCgt6NoZAEYZANcREwLbQZCNpXQZDZD"

		url = reverse("accounts:api_facebook_signup", kwargs = {"version" : "1"})
		data = {
			"accesstoken" : access_token,
		}

		c = Client()
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			if res["error"]["code"] == accounts_errors.FACEBOOK_EXPIRED_ACCESS_TOKEN["code"]:
				ret = False
			else:
				print(res["error"])
				ret = True
		else:
			ret = res["ret"]

		self.assertEqual(error, not ret)



	def test_presignup_step_two(self):
		PRESIGNUPS_ENABLED_ORIGINAL = settings.PRESIGNUPS_ENABLED
		settings.PRESIGNUPS_ENABLED = True
		
		url = reverse("accounts:api_presignup_step_one", kwargs = {"version" : "1"})
		data = {
			"email" : self.test_email_2,
		}

		c = Client()
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(not error, True)
		self.assertEqual(not error, res["ret"])


		presignup = accounts_utils.get_presignup(email = self.test_email_2)
		url = reverse("accounts:api_presignup_step_two", kwargs = {"version" : "1"})
		data = {
			"ide" : presignup.identity,
			"username" : presignup.email,
			"email" : presignup.email,
			"password" : h_utils.random_string(10),
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(not error, True)

		settings.PRESIGNUPS_ENABLED = PRESIGNUPS_ENABLED_ORIGINAL


	def test_presignup_step_one(self):
		PRESIGNUPS_ENABLED_ORIGINAL = settings.PRESIGNUPS_ENABLED
		settings.PRESIGNUPS_ENABLED = True

		url = reverse("accounts:api_presignup_step_one", kwargs = {"version" : "1"})
		data = {
			"email" : self.test_email,
		}
		
		c = Client()
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(not error, res.get("ret", False))

		settings.PRESIGNUPS_ENABLED = PRESIGNUPS_ENABLED_ORIGINAL

		
	def test_reset_password_step_2(self):
		c = Client()
		
		
		url = reverse("accounts:api_reset_password_step_1", kwargs = {"version" : "1"})
		data = {
			"username" : self.test_username,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(not error, True)


		passwordreset = accounts_utils.get_passwordreset(user__username = self.test_username)
		url = reverse("accounts:api_reset_password_step_2", kwargs = {"version" : "1"})
		data = {
			"id" : passwordreset.identity,
			"e" : passwordreset.user.email,
			"password" : h_utils.random_string(10),
		}
		
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(not error, True)

	def test_reset_password_step_1(self):
		c = Client()
		
		
		url = reverse("accounts:api_reset_password_step_1", kwargs = {"version" : "1"})
		data = {
			"username" : self.test_username,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(not error, res.get("ret", False))

	def test_change_password_by_username_failed_by_current_password_equal_to_email(self):
		c = Client()
		c.login(username = self.test_username, password = self.test_password)

		
		url = reverse("accounts:api_change_password", kwargs = {"version" : "1"})
		data = {
			"current" :self.test_password,
			"password" : self.test_email,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if not error and settings.CHECK_PASSWORD_SECURE:
			print("An error was expected but none occured", res)
		
		self.assertEqual(error, settings.CHECK_PASSWORD_SECURE)

	def test_change_password_by_username_failed_by_current_password_equal_to_username(self):
		c = Client()
		c.login(username = self.test_username, password = self.test_password)

		
		url = reverse("accounts:api_change_password", kwargs = {"version" : "1"})
		data = {
			"current" :self.test_password,
			"password" : self.test_username,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if not error and settings.CHECK_PASSWORD_SECURE:
			print("An error was expected but none occured", res)
		
		self.assertEqual(error, settings.CHECK_PASSWORD_SECURE)

	def test_change_password_by_username_failed_by_not_logged_in(self):
		c = Client()
		c.login(username = self.test_username, password = self.test_password)

		
		url = reverse("accounts:api_change_password", kwargs = {"version" : "1"})
		data = {
			"current" : self.test_password,
			"password" : h_utils.random_string(32),
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(error, not res["ret"])

	def test_change_password_by_username_failed_by_new_password_too_short(self):
		c = Client()
		c.login(username = self.test_username, password = self.test_password)

		
		url = reverse("accounts:api_change_password", kwargs = {"version" : "1"})
		data = {
			"current" : self.test_password,
			"password" : h_utils.random_string(3),
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if not error and settings.CHECK_PASSWORD_SECURE:
			print("An error was expected but none occured", res)
		
		self.assertEqual(error, settings.CHECK_PASSWORD_SECURE)

	def test_change_password_by_username_failed_by_current_password(self):
		c = Client()
		c.login(username = self.test_username, password = self.test_password)

		
		url = reverse("accounts:api_change_password", kwargs = {"version" : "1"})
		data = {
			"current" : "invalid-current-password",
			"password" : h_utils.random_string(10),
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if not error:
			print("An error was expected but none occured", res)
		
		self.assertEqual(error, True)
	
	def test_change_password_by_username_success(self):
		c = Client()
		c.login(username = self.test_username, password = self.test_password)

		
		url = reverse("accounts:api_change_password", kwargs = {"version" : "1"})
		data = {
			"current" : self.test_password,
			"password" : h_utils.random_string(10),
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])
		
		self.assertEqual(error, not res["ret"])

	def test_logout_by_username_failed(self):
		c = Client()
		c.login(username = self.test_username, password = self.test_password)

		url = reverse("accounts:api_logout", kwargs = {"version" : "1"})
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		self.assertEqual(error, False)

	def test_logout_by_username_success(self):
		c = Client()
		c.login(username = self.test_username, password = self.test_password)

		
		url = reverse("accounts:api_logout", kwargs = {"version" : "1"})
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		self.assertEqual(not error, res["ret"])

	def test_login_by_email_failed_not_enabled(self):
		ENABLE_EMAIL_LOGIN_ORIGINAL = settings.ENABLE_EMAIL_LOGIN
		settings.ENABLE_EMAIL_LOGIN = False	

		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_email,
			"password" : self.test_password,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		settings.ENABLE_EMAIL_LOGIN = False

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			if res["error"]["code"] == accounts_errors.EMAIL_LOGIN_DISABLED["code"]:
				ret = False
			else:
				print(res["error"])
				ret = True
		else:
			ret = res["ret"]		

		self.assertEqual(error, not ret)
		settings.ENABLE_EMAIL_LOGIN = ENABLE_EMAIL_LOGIN_ORIGINAL

	def test_login_by_email_failed(self):
		ENABLE_EMAIL_LOGIN_ORIGINAL = settings.ENABLE_EMAIL_LOGIN
		settings.ENABLE_EMAIL_LOGIN = True
		

		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_email,
			"password" : "any_password_whatever",
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		settings.ENABLE_EMAIL_LOGIN = False

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if not error:
			print("An error was expected but none occured", res)

		self.assertEqual( error, True)
		settings.ENABLE_EMAIL_LOGIN = ENABLE_EMAIL_LOGIN_ORIGINAL

	def test_login_by_long_email_success(self):
		SIGNUPS_ENABLED_ORIGINAL = settings.SIGNUPS_ENABLED
		settings.SIGNUPS_ENABLED = True

		ENABLE_EMAIL_LOGIN_ORIGINAL = settings.ENABLE_EMAIL_LOGIN
		settings.ENABLE_EMAIL_LOGIN = True
		
		SIGNUP_USERNAME_TRUNCATION_ORIGINAL = settings.SIGNUP_USERNAME_TRUNCATION
		settings.SIGNUP_USERNAME_TRUNCATION = True

		LOGIN_USERNAME_TRUNCATION_ORIGINAL = settings.LOGIN_USERNAME_TRUNCATION
		settings.LOGIN_USERNAME_TRUNCATION = True


		c = Client()
		url = reverse("accounts:api_signup", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_long_email,
			"password" : self.test_long_email_password,
			"email" : self.test_long_email,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)




		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_long_email,
			"password" : self.test_long_email_password,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		settings.ENABLE_EMAIL_LOGIN = False

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, not res["ret"])


		settings.SIGNUPS_ENABLED = SIGNUPS_ENABLED_ORIGINAL
		settings.ENABLE_EMAIL_LOGIN = ENABLE_EMAIL_LOGIN_ORIGINAL
		settings.SIGNUP_USERNAME_TRUNCATION = SIGNUP_USERNAME_TRUNCATION_ORIGINAL
		settings.LOGIN_USERNAME_TRUNCATION = LOGIN_USERNAME_TRUNCATION_ORIGINAL


	def test_login_by_email_success(self):
		ENABLE_EMAIL_LOGIN_ORIGINAL = settings.ENABLE_EMAIL_LOGIN
		settings.ENABLE_EMAIL_LOGIN = True	

		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_email,
			"password" : self.test_password,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		settings.ENABLE_EMAIL_LOGIN = False

		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, not res["ret"])

		settings.ENABLE_EMAIL_LOGIN = ENABLE_EMAIL_LOGIN_ORIGINAL


	def test_login_by_username_success(self):
		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_username,
			"password" : self.test_password,
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, not res["ret"])

	def test_login_by_username_failed(self):
		c = Client()
		url = reverse("accounts:api_login", kwargs = {"version" : "1"})
		
		data = {
			"username" : self.test_username,
			"password" : "any_password_whatever",
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			if res["error"]["code"] == accounts_errors.WRONG_CREDENTIALS["code"]:
				ret = False
			else:
				print(error)
				ret = True

		else:
			ret = res["ret"]

		self.assertEqual(error, not ret)	

	def test_signup_disabled(self):
		SIGNUPS_ENABLED_ORIGINAL = settings.SIGNUPS_ENABLED
		settings.SIGNUPS_ENABLED = False	

		c = Client()
		url = reverse("accounts:api_signup", kwargs = {"version" : "1"})
		
		data = {
			"username" : h_utils.random_string(10),
			"password" : h_utils.random_string(10),
			"email" : "asd@asd.com",
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		settings.SIGNUPS_ENABLED = SIGNUPS_ENABLED_ORIGINAL
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		self.assertEqual(error, True)

	def test_signup_success_with_settings(self):
		
		username = h_utils.random_string(10)
		password = h_utils.random_string(10)
		email = h_utils.random_string(10) + "@" + h_utils.random_string(5) + ".com"

		settings_tmp = {
			"country" : countries_utils.get_country(code = "CL"),
			"currency" : currencies_utils.get_currency(code = "CLP"),
			"timezone" : settings.DEFAULT_TZ,
			"language" : "es",
			"change_password" : False,
			"email_validated" : False,
		}
		user = accounts_utils.create_user(username, email, password, settings = settings_tmp)
		self.assertEqual(True, True)
		
		
	def test_signup_success(self):
		SIGNUPS_ENABLED_ORIGINAL = settings.SIGNUPS_ENABLED
		settings.SIGNUPS_ENABLED = True	

		c = Client()
		url = reverse("accounts:api_signup", kwargs = {"version" : "1"})
		
		data = {
			"username" : h_utils.random_string(10),
			"password" : h_utils.random_string(10),
			"email" : "asd@asd.com",
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if error:
			print(res["error"])

		self.assertEqual(error, False)	
		settings.SIGNUPS_ENABLED = SIGNUPS_ENABLED_ORIGINAL
			
	def test_signup_username_too_long(self):
		c = Client()
		url = reverse("accounts:api_signup", kwargs = {"version" : "1"})
		
		data = {
			"username" : h_utils.random_string( settings.MAX_USERNAME_LENGTH + 1),
			"password" : h_utils.random_string(10),
			"email" : "asd@asd.com",
		}
		response = c.post(url, data = json.dumps(data), content_type = 'application/json')
		self.assertEqual(response.status_code, 200)
		res = json.loads(response.content)
		error = True if res["error"] else False
		if not error and settings.CHECK_PASSWORD_SECURE:
			print("An error was expected but none occured", res)
		
		self.assertEqual(error, settings.CHECK_PASSWORD_SECURE)

	def test_signup_password_not_safe_no_user(self):
		PRESIGNUPS_ENABLED_ORIGINAL = settings.PRESIGNUPS_ENABLED
		settings.PRESIGNUPS_ENABLED = False

		CHECK_PASSWORD_SECURE_ORIGINAL = settings.CHECK_PASSWORD_SECURE
		settings.CHECK_PASSWORD_SECURE = True

		c = Client()
		url = reverse("accounts:api_signup", kwargs = {"device" : "android", "version" : "1"})
		
		
		min_length = 1
		for v in settings.AUTH_PASSWORD_VALIDATORS:
			if v["NAME"] == 'django.contrib.auth.password_validation.MinimumLengthValidator':
				min_length = v["OPTIONS"]["min_length"]

		to_check = [
			{"u" : "asd", "p" : h_utils.random_string(min_length - 1), "e" : "asd@asd.com", "r" : True},
			{"u" : "asd", "p" : h_utils.random_string(min_length), "e" : "asd@asd.com", "r" : False},
		]
		for check in to_check:
			data = {
				"username" : check["u"],
				"password" : check["p"],
				"email" : check["e"],
			}
			response = c.post(url, data = json.dumps(data), content_type = 'application/json')
			self.assertEqual(response.status_code, 200)
			res = json.loads(response.content)
			error = True if res["error"] else False
			if error and not check["r"]:
				print(res["error"])

			self.assertEqual(error, check["r"])	

		settings.PRESIGNUPS_ENABLED = PRESIGNUPS_ENABLED_ORIGINAL
		settings.CHECK_PASSWORD_SECURE = CHECK_PASSWORD_SECURE_ORIGINAL

		
	def setUp(self):
		h_settings.PRINT_BASE_ERRORS = False

		call_command('countries_init')
		call_command('currencies_init')

		user = accounts_utils.create_user(self.test_username, self.test_email, self.test_password)		
		alias = accounts_utils.create_alias(user, self.test_alias)

		