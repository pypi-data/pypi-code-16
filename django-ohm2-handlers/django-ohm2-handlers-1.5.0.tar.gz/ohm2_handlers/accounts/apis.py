from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from . import apisdispatcher as dispatcher


@api_view(['POST'])
@permission_classes((AllowAny,))
def signup(request, version):
	keys = [
		("username", "username", ""),
		("password", "password", ""),
		("email", "email", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.signup, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@permission_classes((AllowAny,))
def signup_and_get_token(request, version):
	keys = [
		("username", "username", ""),
		("password", "password", ""),
		("email", "email", ""),
	]
	res, error = dispatcher.view_base_data(request, version, "POST", dispatcher.signup_and_get_token, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def facebook_signup(request, version):
	keys = [
		("access_token", "accesstoken", ""),
		#("email", "email", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.facebook_signup, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@permission_classes((AllowAny,))
def facebook_signup_and_get_token(request, version):
	keys = [
		("access_token", "accesstoken", ""),
	]
	res, error = dispatcher.view_base_data(request, version, "POST", dispatcher.facebook_signup_and_get_token, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request, version):
	keys = [
		("username", "username", ""),
		("password", "password", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.login, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_and_get_token(request, version):
	keys = [
		("username", "username", ""),
		("password", "password", ""),
	]
	res, error = dispatcher.view_base_data(request, version, "POST", dispatcher.login_and_get_token, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(res)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def logout(request, version):
	keys = [
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.logout, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)

@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def change_password(request, version):
	keys = [
		("current", "current", ""),
		("password", "password", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.change_password, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@permission_classes((AllowAny,))
def reset_password_step_1(request, version):
	keys = [
		("username", "username", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.reset_password_step_1, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@permission_classes((AllowAny,))
def reset_password_step_2(request, version):
	keys = [
		("identity", "id", ""),
		("code", "code", ""),
		("email", "e", ""),
		("password", "password", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.reset_password_step_2, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@permission_classes((AllowAny,))
def signup_and_login(request, version):
	keys = [
		("username", "username", ""),
		("password", "password", ""),
		("email", "email", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.signup, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	elif ret.get("error"):
		return JsonResponse(ret)

	keys = [
		("username", "username", ""),
		("password", "password", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.login, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def update_avatars(request, version):
	ret, error = dispatcher.view_update_avatars(request, version)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def update_settings(request, version):
	keys = [
		("country", "country", ""),
		("currency", "currency", ""),
		("timezone", "timezone", ""),
		("language", "language", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.update_settings, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)



@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def update_user_password(request, version):
	keys = [
		("current_password", "currentPassword", ""),
		("new_password", "newPassword", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.update_user_password, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@permission_classes((AllowAny,))
def presignup_step_one(request, version):
	keys = [
		("email", "email", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.presignup_step_one, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@permission_classes((AllowAny,))
def presignup_step_two(request, version):
	keys = [
		("identity", "ide", ""),
		("username", "username", ""),
		("email", "email", ""),
		("password", "password", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.presignup_step_two, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)



@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def update_user_information(request, version):
	keys = [
		("first_name", "first_name", ""),
		("last_name", "last_name", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.update_user_information, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)



@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def update_alias(request, version):
	keys = [
		("name", "name", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.update_alias, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)