from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from ohm2_handlers import managers as handlers_managers
from ohm2_handlers import settings


class BaseModel(models.Model):
	identity = models.CharField(max_length=settings.STRING_DOUBLE, unique = True)
	created = models.DateTimeField(default = timezone.now)
	last_update = models.DateTimeField(default = timezone.now)
	
	objects = handlers_managers.HandlersManager()

	def __str__(self):
		return self.identity

	class Meta:
		abstract = True


class BaseError(BaseModel):
	app = models.CharField(max_length=settings.STRING_DOUBLE)
	code = models.IntegerField(default = -1)
	message = models.TextField(default = "")
	extra = models.TextField(default = "")
	
	ins_filename = models.CharField(max_length=settings.STRING_DOUBLE, null = True, blank = True, default = "")
	ins_lineno = models.IntegerField(null = True, blank = True, default = 0)
	ins_function = models.CharField(max_length=settings.STRING_DOUBLE, null = True, blank = True, default = "")
	ins_code_context = models.TextField(null = True, blank = True, default = "")

	def __str__(self):
		return "{0}|{1}|{2}|{3}".format(self.identity, self.app, self.code, self.message)


class BaseEmail(BaseModel):
	provider = models.CharField(max_length=settings.STRING_DOUBLE)
	to_email = models.EmailField()
	from_email = models.EmailField()
	subject = models.CharField(max_length=settings.STRING_DOUBLE)
	html = models.TextField(default = "")
	text = models.TextField(default = "")

	sent = models.BooleanField(default = False)
	read = models.BooleanField(default = False)

	extra = models.TextField(default = "")
	
	def __str__(self):
		return "{0}|{1}|{2}|{3}|{4}".format(self.identity, self.to_email, self.subject, self.sent, self.read)


class Statistics(BaseModel):
	total_requests = models.PositiveIntegerField()
	average_request_time = models.PositiveIntegerField()
	


class LandingMessage(BaseModel):
	name = models.CharField(max_length=settings.STRING_DOUBLE)
	subject = models.CharField(max_length=settings.STRING_DOUBLE)
	message = models.TextField()
	ip_address = models.GenericIPAddressField()


class LandingEmail(BaseModel):
	email = models.EmailField()
	ip_address = models.GenericIPAddressField()


class ContactMessage(BaseModel):
	s_other = (1, "Other")
	s_support = (2, "Support")
	s_bug_report = (3, "Bug report")
	s_Feature_request = (4, "Feature request")
	s_information = (5, "Information")
	s_inquiries = (6, "Inquiries")

	subjects = (
		s_other,
		s_support,
		s_bug_report,
		s_Feature_request,
		s_information,
		s_inquiries,
	)
	subject = models.IntegerField(choices = subjects, default = s_other[0])
	email = models.EmailField()
	message = models.TextField()
	ip_address = models.GenericIPAddressField()		