from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers.models import BaseModel
from ohm2_handlers import utils as h_utils
from ohm2_handlers.currencies import models as currencies_models
from ohm2_handlers.countries import models as countries_models
from . import managers
from . import settings
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from Crypto.Cipher import AES
import pytz, base64



class Presignup(BaseModel):
	email = models.EmailField(unique = True)
	last_sent = models.DateTimeField(null = True, blank = True, default = None)
	activation_date = models.DateTimeField(null = True, blank = True, default = None)

	def send_again(self):
		if self.last_sent and not h_utils.is_older_than_now(self.last_sent, seconds = 10):
			return False
		return True



class Settings(BaseModel):
	timezones = sorted( tuple( [ (tz, tz) for tz in pytz.common_timezones] ), key = lambda tup: tup[1] )
	languages = sorted( tuple( [lang for lang in settings.LANGUAGES] ), key = lambda tup: tup[1] )

	user = models.OneToOneField(User, on_delete = models.CASCADE)
	currency = models.ForeignKey(currencies_models.Currency)
	country = models.ForeignKey(countries_models.Country)
	timezone = models.CharField(max_length = settings.STRING_NORMAL, choices = timezones)
	language = models.CharField(max_length = settings.STRING_NORMAL, choices = languages, default=settings.LANGUAGE_CODE)
		
	change_password = models.BooleanField(default = False)
	email_validated = models.BooleanField(default = False)
	
	def __str__(self):
		return self.user.username


class Keys(BaseModel):
	user = models.OneToOneField(User, on_delete = models.CASCADE)

	private_1024 = models.CharField(max_length = settings.STRING_DOUBLE, unique = True)
	public_1024 = models.CharField(max_length = settings.STRING_DOUBLE, unique = True)

	private_2048 = models.CharField(max_length = settings.STRING_DOUBLE, unique = True)
	public_2048 = models.CharField(max_length = settings.STRING_DOUBLE, unique = True)



class Avatars(BaseModel):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	original = models.ImageField(upload_to = managers.avatars_upload_to)
	o_25x25 = ImageSpecField(source='original', processors=[ResizeToFill(25, 25)], format='JPEG', options={'quality': 75})
	o_50x50 = ImageSpecField(source='original', processors=[ResizeToFill(50, 50)], format='JPEG', options={'quality': 75})
	o_75x75 = ImageSpecField(source='original', processors=[ResizeToFill(75, 75)], format='JPEG', options={'quality': 75})
	o_100x100 = ImageSpecField(source='original', processors=[ResizeToFill(100, 100)], format='JPEG', options={'quality': 75})
	o_125x125 = ImageSpecField(source='original', processors=[ResizeToFill(125, 125)], format='JPEG', options={'quality': 75})
	o_150x150 = ImageSpecField(source='original', processors=[ResizeToFill(150, 150)], format='JPEG', options={'quality': 75})
	o_200x200 = ImageSpecField(source='original', processors=[ResizeToFill(200, 200)], format='JPEG', options={'quality': 75})
	o_250x250 = ImageSpecField(source='original', processors=[ResizeToFill(250, 250)], format='JPEG', options={'quality': 75})
	o_350x350 = ImageSpecField(source='original', processors=[ResizeToFill(350, 350)], format='JPEG', options={'quality': 75})


class PasswordReset(BaseModel):
	user = models.ForeignKey(User)
	last_sent_date = models.DateTimeField(null = True, blank = True, default = None)
	activation_date = models.DateTimeField(null = True, blank = True, default = None)

	ip = models.GenericIPAddressField(null = True, blank = True, default = "")

	code = models.CharField(max_length = settings.STRING_NORMAL)

	def send_again(self):
		if self.last_sent_date and not h_utils.is_older_than_now(self.last_sent_date, seconds = settings.MINIMUM_PASSWORD_RESET_DELAY):
			return False
		return True

	def __str__(self):
		return self.user.username



class ReferalCode(BaseModel):
	user =  models.ForeignKey(User, on_delete = models.CASCADE)
	code = models.CharField(max_length = settings.STRING_NORMAL, unique = True)

	def __str__(self):
		return self.user.username + "|" + self.code



class Crypto(BaseModel):
	user = models.OneToOneField(User, on_delete = models.CASCADE)

	key_16 = models.CharField(max_length = settings.STRING_DOUBLE)
	mode_16 = models.IntegerField(default = AES.MODE_CFB)
	iv_16 = models.CharField(max_length = settings.STRING_DOUBLE)

	def decrypt_16(self, cipher):
		obj = AES.new(self.key_16, self.mode_16, base64.b64decode(self.iv_16))
		return obj.decrypt(cipher).strip()

	def encrypt_16(self, message):
		obj = AES.new(self.key_16, self.mode_16, base64.b64decode(self.iv_16))
		return obj.encrypt(message)


class Alias(BaseModel):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	name = models.CharField(max_length = settings.STRING_NORMAL, unique = True)



