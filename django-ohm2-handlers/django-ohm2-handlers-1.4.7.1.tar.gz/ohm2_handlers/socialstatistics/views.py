from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from . import viewsdispatcher as dispatcher


def index(request):
	keys = [
	]
	ret, error = dispatcher.view_base(request, "GET", dispatcher.index, keys)
	if error:
		return redirect("/")
	request.context["ret"] = ret	
	request.context["template"] = "index"
	return render(request, "socialstatistics/base_template.html", request.context)
