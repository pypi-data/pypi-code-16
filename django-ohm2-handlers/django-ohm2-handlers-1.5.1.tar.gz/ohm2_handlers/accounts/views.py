from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from . import viewsdispatcher as dispatcher


@login_required
def logout(request):
	ret, error = dispatcher.view_base(request, "GET", dispatcher.logout, [])
	if error:
		return redirect("/")
	return redirect("/")


def presignup_step_one(request):
	if request.user.is_authenticated():
		return redirect("/")
	
	keys = [
		("email", "email", ""),
	]
	return dispatcher.view_base(request, "POST", dispatcher.presignup_step_one, keys)


def presignup_step_two(request):
	if request.user.is_authenticated():
		return redirect("/")

	return dispatcher.view_presignup_step_two(request)


@login_required
def check_user_integrity_and_redirect(request):
	keys = [
		("next", "next", "/"),
	]
	ret, error = dispatcher.view_base(request, "GET", dispatcher.check_user_integrity_and_redirect, keys)
	if error:
		return redirect("/")
	return redirect( ret["next"] )

