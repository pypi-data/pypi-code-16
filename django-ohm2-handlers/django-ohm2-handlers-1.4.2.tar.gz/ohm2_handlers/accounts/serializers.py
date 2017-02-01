from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers
from ohm2_handlers.accounts import models
from easy_thumbnails.files import get_thumbnailer
from . import settings



class User(serializers.ModelSerializer):
	class Meta:
		model = AuthUser
		fields = (
			'username',
			'email',
			'last_name',
			'first_name',
		)


class ImageRatioField(serializers.Field):


	def __init__(self, *args, **kwargs):
		self.spec_field = kwargs.pop("spec_field")
		super(ImageRatioField, self).__init__(*args, **kwargs)
		
	def to_representation(self, obj):
		if obj.original:
			try:
				cropped_url = settings.AVATARS_WEBSITE_URL + get_thumbnailer(obj.original).get_thumbnail({
				    'size': (obj.original.width, obj.original.height),
				    'box': getattr(obj, self.spec_field),
				    'crop': True,
				    'detail': True,
				}).url
			except Exception as e:
				cropped_url = None
		
		else:
			cropped_url = None


		return settings.AVATARS_WEBSITE_URL + cropped_url

	def get_attribute(self, obj):
		return obj	

class ImageSpecField(serializers.Field):

	def __init__(self, *args, **kwargs):
		self.spec_field = kwargs.pop("spec_field")
		super(ImageSpecField, self).__init__(*args, **kwargs)
		
	def to_representation(self, obj):
		if obj.original:
			try:
				url = settings.AVATARS_WEBSITE_URL + getattr(obj, self.spec_field).url
			except Exception as e:
				url = None	
		else:
			url = None

		return url

	def get_attribute(self, obj):
		return obj

class Avatars(serializers.ModelSerializer):

	o_25x25 = ImageSpecField(spec_field = "o_25x25")
	o_50x50 = ImageSpecField(spec_field = "o_50x50")
	o_75x75 = ImageSpecField(spec_field = "o_75x75")
	o_100x100 = ImageSpecField(spec_field = "o_100x100")
	o_125x125 = ImageSpecField(spec_field = "o_125x125")
	o_150x150 = ImageSpecField(spec_field = "o_150x150")
	o_200x200 = ImageSpecField(spec_field = "o_200x200")
	o_250x250 = ImageSpecField(spec_field = "o_250x250")
	o_350x350 = ImageSpecField(spec_field = "o_350x350")

	class Meta:
		model = models.Avatars
		fields = (
			'identity',
			'created',
			'last_update',
			'o_25x25',
			'o_50x50',
			'o_75x75',
			'o_100x100',
			'o_125x125',
			'o_150x150',
			'o_200x200',
			'o_250x250',
			'o_350x350',
		)
