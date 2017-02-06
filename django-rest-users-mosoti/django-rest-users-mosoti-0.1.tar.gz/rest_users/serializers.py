from rest_framework import serializers
from django.contrib.auth.models import Permission,Group
from django.contrib.contenttypes.models import ContentType

from .models import User
class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ContentType
        fields='__all__'


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Permission
        fields='__all__'

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        depth=1
        model=Group
        fields='__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields='__all__'
        extra_kwargs={'password':{'write_only':True}}
       
    def create(self,validated_data): 
        email=validated_data.pop('email')
        password=validated_data.pop('password')
        return User.objects.create_user(email=email,password=password,**validated_data)
         
class UserChangePasswordSerializer(serializers.Serializer):
    old_password=serializers.CharField(max_length=50,write_only=True)
    new_password=serializers.CharField(max_length=50,write_only=True)
    new_password_again=serializers.CharField(max_length=50,write_only=True)
  
    

class UserResetPasswordSerializer(serializers.Serializer):
    email=serializers.CharField(max_length=50,write_only=True)
   

class UserVerifyEmailSerializer(serializers.Serializer):
    verification_code=serializers.CharField(max_length=50,write_only=True)
   