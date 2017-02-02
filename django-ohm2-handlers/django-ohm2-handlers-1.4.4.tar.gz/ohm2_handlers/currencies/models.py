from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers.models import BaseModel
from . import managers
from . import settings
import pycountry



class Currency(BaseModel):
	code_choices = sorted( tuple( [ (c.alpha_3, c.name) for c in list(pycountry.currencies)] ), key = lambda tup: tup[1] )
	
	code = models.CharField(max_length = settings.STRING_SHORT, choices = code_choices)
	name = models.CharField(max_length = settings.STRING_DOUBLE)
	symbol = models.CharField(max_length = settings.STRING_SHORT)
	decimals = models.PositiveIntegerField()
	
	active = models.BooleanField(default = True)
		
	def __str__(self):
		return self.code + '|' + self.symbol

	

class ConvertionRate(BaseModel):
	code_choices = sorted( tuple( [ (c.alpha_3, c.name) for c in list(pycountry.currencies)] ), key = lambda tup: tup[1] )

	input = models.ForeignKey(Currency, related_name = 'input_currency')
	output = models.ForeignKey(Currency, related_name = 'output_currency')
	source = models.CharField(max_length = settings.STRING_DOUBLE)
	rate = models.FloatField()
	
	def __str__(self):
		return '1 ' + self.input.code + ' = {} '.format(self.rate) + self.output.code


class LastConvertionRate(BaseModel):
	convertion_rate = models.OneToOneField(ConvertionRate)

	def __str__(self):
		return '(this)-->([{}] '.format(self.convertion_rate.id) + self.convertion_rate.__str__() + ')'



