from django.shortcuts import render
from django.http import JsonResponse, Http404
from djangoApiDec.djangoApiDec import queryString_required
from django.core import serializers
from django.forms.models import model_to_dict
from slothTw.models import *
import json

# Create your views here.
@queryString_required(['school', 'start'])
def clist(request):
	result = Course.objects.filter(school=request.GET['school'])[int(request.GET['start']):int(request.GET['start'])+15]
	return JsonResponse(json.loads(serializers.serialize('json', list(result), fields=('name', 'avatar', 'teacher'))), safe=False)

@queryString_required(['school', 'name', 'teacher'])
def cvalue(request):
	try:
		result = model_to_dict(Course.objects.get(school=request.GET['school'], name=request.GET['name'],teacher=request.GET['teacher']))
		result['avatar'] = result['avatar'].url if result['avatar'] else None
		return JsonResponse(result, safe=False)
	except Exception as e:
		raise

@queryString_required(['school', 'name', 'teacher', 'start'])
def cComment(request):
	try:
		start = int(request.GET['start']) - 1
		c = Course.objects.get(school=request.GET['school'], name=request.GET['name'],teacher=request.GET['teacher'])
		result = c.comment_set.all()[start:start+15]
		return JsonResponse(json.loads(serializers.serialize('json', list(result))), safe=False)
	except Exception as e:
		raise


@queryString_required(['school', 'name', 'teacher'])
def reply(request):
	try:
		c = Course.objects.get(school=request.GET['school'], name=request.GET['name'],teacher=request.GET['teacher'])
		Comment.objects.create(course=c, raw=request.POST['reply'])
		return JsonResponse({'success':True})
	except Exception as e:
		raise Http404('reply error')