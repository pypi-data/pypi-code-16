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
def create_landing_message(request, version):
	keys = [
		("name", "name", ""),
		("subject", "subject", ""),
		("message", "message", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.create_landing_message, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)

@api_view(['POST'])
@permission_classes((AllowAny,))
def create_landing_email(request, version):
	keys = [
		("email", "email", ""),
	]
	ret, error = dispatcher.view_base_data(request, version, "POST", dispatcher.create_landing_email, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)