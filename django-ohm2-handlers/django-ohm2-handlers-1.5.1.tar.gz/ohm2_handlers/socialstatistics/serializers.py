from django.contrib.auth.models import User as AuthUser
from rest_framework import serializers
from . import models
from . import settings



#class Serializer(serializers.ModelSerializer):
#	class Meta:
#		model = models.Model
#		fields = (
#			'identity',
#			'created',
#			'last_update',
#		)