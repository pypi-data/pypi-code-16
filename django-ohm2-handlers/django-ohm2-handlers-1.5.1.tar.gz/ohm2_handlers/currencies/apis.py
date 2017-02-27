from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from . import apisdispatcher as dispatcher


def index(request, version):
	keys = [
	]
	ret, error = dispatcher.view_base(request, version, "GET", dispatcher.index, keys)
	if error:
		return JsonResponse({"error" : error.regroup()})
	return JsonResponse(ret)

