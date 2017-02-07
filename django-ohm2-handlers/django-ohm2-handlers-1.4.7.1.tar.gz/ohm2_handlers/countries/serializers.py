from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers
from . import models
from . import settings



class Country(serializers.ModelSerializer):
	class Meta:
		model = models.Country
		fields = (
			'identity',
			'created',
			'last_update',
			'code',
			'name',
		)


class Region(serializers.ModelSerializer):

	country = Country()

	class Meta:
		model = models.Region
		fields = (
			'identity',
			'created',
			'last_update',
			'country',
			'code',
			'name',
		)



class Province(serializers.ModelSerializer):

	region = Region()

	class Meta:
		model = models.Province
		fields = (
			'identity',
			'created',
			'last_update',
			'region',
			'code',
			'name',
		)		



class Commune(serializers.ModelSerializer):

	province = Province()

	class Meta:
		model = models.Commune
		fields = (
			'identity',
			'created',
			'last_update',
			'province',
			'code',
			'name',
		)	


class UserAddress(serializers.ModelSerializer):

	region = Region()
	commune = Commune()

	class Meta:
		model = models.Commune
		fields = (
			'identity',
			'created',
			'last_update',
			'region',
			'commune',
			'street',
			'number',
			'apartment',
			'extra_information',
			'latitude',
			'longitude',
		)