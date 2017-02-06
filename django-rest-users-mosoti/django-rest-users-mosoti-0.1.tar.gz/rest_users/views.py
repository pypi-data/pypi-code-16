
import random,string

from django.db import transaction
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import Permission,Group
from django.contrib.contenttypes.models import ContentType



from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.parsers import FormParser, MultiPartParser,JSONParser
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import filters

from .serializers import *
from .models import User,Code,ResetPassword
from rest_utils.renderers import CustomJSONRenderer
from rest_utils.views import TransactionalViewMixin


class UserPermissionsList(TransactionalViewMixin,generics.ListCreateAPIView):
    
    #error_message =" "
    #success_messgae = ""

    serializer_class=UserPermissionSerializer
    renderer_classes = (CustomJSONRenderer, )
   
    search_fields=('codename','name',)

    def perform_create(self,serializer):
        serializer.save()

    def get_queryset(self):
        return Permission.objects.all()



class UserGroupList(TransactionalViewMixin,generics.ListCreateAPIView):
    #error_message =" "
    #success_messgae = ""
    serializer_class=UserGroupSerializer
    renderer_classes = (CustomJSONRenderer, )
   
    def perform_create(self,serializer):
        serializer.save()

    def get_queryset(self):
        return Group.objects.all()

class ContentTypeList(TransactionalViewMixin,generics.ListCreateAPIView):
   
    #error_message =" "
    #success_messgae = ""
    serializer_class=ContentTypeSerializer
    renderer_classes = (CustomJSONRenderer, )
    def perform_create(self,serializer):
        serializer.save()
    def get_queryset(self):
        return ContentType.objects.all()


class UserList(TransactionalViewMixin,generics.ListCreateAPIView):
    """ used for user signup """
    #error_message =" "
    #success_messgae = ""
    serializer_class=UserSerializer
    renderer_classes = (CustomJSONRenderer, )
    permission_classes = (AllowAny,)
    authentication_classes = ()
    
    filter_fields = ('first_name','last_name','email',)
    
    search_fields=('first_name','last_name','email',)
    
    def perform_create(self,serializer):
        serializer.save()

    def get_queryset(self):
        return User.objects.filter(is_active=True)
    


class UserDetail(TransactionalViewMixin,generics.RetrieveUpdateAPIView):
    """ you can also mmake partial updates using PUT. 
    if password field is provided, the password will change. but no email/ notification will be sent to User
    regarding the changes
    """
    serializer_class=UserSerializer
    parser_classes = (MultiPartParser, FormParser,JSONParser)
    renderer_classes = (CustomJSONRenderer, )
    queryset=User.objects.all()

    def put(self, request, pk, format=None):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            valid_data = serializer.validated_data
            serializer.save()
            if valid_data.get('password'):
                user.set_password(valid_data.get('password'))
                user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self,model_object):
        model_object.is_active=True
        model_object.save()


class UserChangePassword(TransactionalViewMixin,generics.CreateAPIView):
    """To change password, enter the required fields old_password,new_password,new_password_again and user.
    user will receive an email of the notification on successful reset
    """
    
    serializer_class=UserChangePasswordSerializer
    
    renderer_classes = (CustomJSONRenderer, )
    error_message="All the fields are required"
    success_message="Your password was changed succesfully."
    
    
    def post(self, request,format=None):
        serializer = UserChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            valid_data=serializer.validated_data
            #chec if passwords match
            user=request.user

            old_password=valid_data.get('old_password')
            new_password=valid_data.get('new_password')
            new_password_again=valid_data.get('new_password_again')
            if new_password != new_password_again:
                #passwords do not match . fail
                self.error_message="Please enter the same password twice."
                raise serializers.ValidationError({'new_password':"Passwords do not match",
                                                   'new_password_again':"Passwords do not match"})
            
            #check if user with this password exists
            if not user.check_password(old_password):
                #not found
                self.error_message="Please enter your correct  password."
                raise serializers.ValidationError({'old_password':"Incorrect password"})
         
            #change password here also verify email if user is same.
            user.set_password(new_password)
            user.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    

    
    
class UserResetPassword(TransactionalViewMixin,generics.CreateAPIView):
    
    """
    Uses only POST
    email field is required.
    To reset password after email request you need:
    reset_code,new_password,email,new_password_again fields. 
    To request for a reset of password: 
    you required email field only.
    """
    permission_classes = (AllowAny,)
    serializer_class=UserResetPasswordSerializer
    renderer_classes = (CustomJSONRenderer, )
    authentication_classes = ()
    error_message="Oops something went wrong"
    success_message="Success"
    
    def post(self, request,format=None):
        serializer = UserResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            valid_data=serializer.validated_data
            email=valid_data.get('email')
            try:
                user=User.objects.get(email=email)
                reset_code  = self.get_reset_code()
                user.set_password(reset_code)
                user.is_active = True
                self.send_default_pass(user,reset_code)
                user.save()
                self.success_message = "We sent you a temporary passcode./Please use it as a temporary password"
                return Response(serializer.data)
            except:
                self.error_message="Oops please check that your email is correct."
                raise serializers.ValidationError({'email':"User with this email Does not exist !"})
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_reset_code(self):
        return  ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))


    def send_default_pass(self,user,reset_code):
        r_message = "We received your password reset request.Please use %s  as your defualt password.\
        " % (reset_code)
        return True



  

class UserVerifyEmail(TransactionalViewMixin,generics.ListCreateAPIView):
    """To verify email. For sending code, use GET for veification of the code received in email use POST
    For logged in users. 
    """
    
    serializer_class=UserVerifyEmailSerializer
    
    renderer_classes = (CustomJSONRenderer, )
    error_message="All the fields are required"
    success_message="Succesfully."
    
    def get_queryset(self):
        #send email verification code for looged in use 
        user=self.request.user
        code=Code.generate(user=user,reason=Code.EMAIL_VERIFICATION)
        #send mail
        r_message="To verify your email enter the code : %s "%(code.code)
        self.success_message='Email verification code sent.'
        return []

    
    def post(self, request,format=None):
        serializer = UserVerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            valid_data=serializer.validated_data
            #chec if passwords match
            user=request.user
            verification_code=valid_data.get('verification_code')
            code=Code.is_valid(user=user,reason=Code.EMAIL_VERIFICATION,code=verification_code)
            if code:
                #valid 
                user.is_email_verified=True
                user.save()
                self.success_message="Email verified"
                #remove the Code
                code.delete()
            else:
                #incorrect options for verifiyn
                raise serializers.ValidationError({'verification_code':"The code is invalid."})
                self.error_message="Please enter correct code"

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
