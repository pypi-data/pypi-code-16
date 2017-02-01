from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from . import apisdispatcher as dispatcher


@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def twitter_authorization_url(request, version):
	ret, error = dispatcher.view_base(request, version, "GET", dispatcher.twitter_authorization_url, [])
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)



@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def twitter_get_access_token(request, version):
	keys = [
		("oauth_token", "oauth_token", ""),
		("oauth_verifier", "oauth_verifier", ""),
	]
	res, error = dispatcher.view_base(request, version, "GET", dispatcher.twitter_get_access_token, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	elif res["error"]:
		return JsonResponse({"error" : res["error"]})

	ret = res["ret"]	
	return redirect(ret)



@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def facebook_authorization_url(request, version):
	ret, error = dispatcher.view_base(request, version, "GET", dispatcher.facebook_authorization_url, [])
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)



@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def facebook_get_access_token(request, version):
	keys = [
		("code", "code", ""),
	]
	res, error = dispatcher.view_base(request, version, "GET", dispatcher.facebook_get_access_token, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	elif res["error"]:
		return JsonResponse({"error" : res["error"]})

	ret = res["ret"]	
	return redirect(ret)



@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def twitter_delete_account(request, version):
	keys = [
		("identity", "id", ""),
	]
	ret, error = dispatcher.view_base(request, version, "POST", dispatcher.twitter_delete_account, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)



@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def facebook_delete_account(request, version):
	keys = [
		("identity", "id", ""),
	]
	ret, error = dispatcher.view_base(request, version, "POST", dispatcher.facebook_delete_account, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def facebook_delete_page(request, version):
	keys = [
		("identity", "id", ""),
	]
	ret, error = dispatcher.view_base(request, version, "POST", dispatcher.facebook_delete_page, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def facebook_create_page(request, version):
	keys = [
		("facebook", "fid", ""),
		("page_id", "pid", ""),
	]
	ret, error = dispatcher.view_base(request, version, "POST", dispatcher.facebook_create_page, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)

