from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers.models import BaseModel
from . import managers
from . import settings
import pycountry



class Country(BaseModel):
	code_choices = sorted( tuple( [ (c.alpha_2, c.name) for c in list(pycountry.countries)] ), key = lambda tup: tup[1] )
	
	code = models.CharField(max_length = settings.STRING_SHORT, choices = code_choices)
	name = models.CharField(max_length = settings.STRING_DOUBLE)
	
	
	def __str__(self):
		return self.code + '|' + self.name

	class Meta:
		verbose_name_plural = "Countries"
		ordering = ["name", "code"]	



class Region(BaseModel):
	country = models.ForeignKey(Country, on_delete = models.CASCADE)
	code = models.CharField(max_length = settings.STRING_SHORT)
	name = models.CharField(max_length = settings.STRING_DOUBLE)

	def __str__(self):
		return self.identity + '|' + self.code + '|' + self.name

class Province(BaseModel):
	region = models.ForeignKey(Region, on_delete = models.CASCADE)
	name = models.CharField(max_length = settings.STRING_DOUBLE)
	code = models.CharField(max_length = settings.STRING_SHORT)

	def __str__(self):
		return self.identity + '|' + self.code + '|' + self.name

class Commune(BaseModel):
	province = models.ForeignKey(Province, on_delete = models.CASCADE)
	code = models.CharField(max_length = settings.STRING_SHORT)
	name = models.CharField(max_length = settings.STRING_DOUBLE)
	
	def __str__(self):
		return self.identity + '|' + self.code + '|' + self.name
		
class UserAddress(BaseModel):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	region = models.ForeignKey(Region, on_delete = models.CASCADE, null = True, blank = True, default = None)
	commune = models.ForeignKey(Commune, on_delete = models.CASCADE, null = True, blank = True, default = None)
	street = models.CharField(max_length = settings.STRING_NORMAL)
	number = models.CharField(max_length = settings.STRING_NORMAL)
	apartment = models.CharField(max_length = settings.STRING_SHORT, null = True, blank = True, default = "")
	extra_information = models.TextField(null = True, blank = True, default = "")
	latitude = models.FloatField(default = 0.0)
	longitude = models.FloatField(default = 0.0)

	apartment_abbreviation = "depto"

	@property
	def formated_address(self):
		address = self.street

		if len(self.number) > 0:
			address += " " + self.number

		if len(self.apartment) > 0:
			address += ", " + self.apartment_abbreviation + " " + self.apartment
		
		if self.commune:
			address += ", " + self.commune.name

		if self.region:
			address += ", " + self.region.name	


		return address