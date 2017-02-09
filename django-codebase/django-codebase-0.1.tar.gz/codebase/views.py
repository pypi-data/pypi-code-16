from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *

# Create your views here.
def index(request):
    return render(request, 'codebase/index.html', {})


def decode_dict(dict1):
    keys = dict1.keys()
    for key in keys:
	print "key is",key
	print "value is",dict1[key]
	if type(dict1[key]) == dict:
	    decode_dict(dict1[key])
    return ""

@csrf_exempt
def a_create_api(request):
    #~ import ipdb;ipdb.set_trace()

    url = request.POST.get("url",None)
    params = request.POST.get("params",None)
    desc = request.POST.get("desc",'')
    http_type = request.POST.get("http_type",None)
    
    api = Api()
    api.url = url
    api.params = params
    api.desc = desc
    api.http_type = http_type
    api.save()
    
    
    
    #~ print url,params
    #~ p2 = eval(params)
    #~ if type(p2) == dict:
	#~ decode_dict(p2)
	#~ keys = p2.keys()  
	    
    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")

@csrf_exempt
def a_get_apis(request):
    params = '{"k1":"v1","k2":"v2"}'
    params2 = '{"k1":["v1","v2","v3"],"k2":{"k3":"v3"}}'
    
    
    objs = [{"url":"/a_create_api/","params":eval(params2)}]
    
    
    list1 = []
    
    for api in Api.objects.all():
	dict2 = {}
	dict2["url"] = api.url
	dict2["params"] = eval(api.params)
	dict2["http_type"] = api.http_type
	list1.append(dict2)
    
    dict1={}
    dict1["result"] = "Success"
    dict1["response"] = list1
    return HttpResponse(json.dumps(dict1),content_type="application/json")










