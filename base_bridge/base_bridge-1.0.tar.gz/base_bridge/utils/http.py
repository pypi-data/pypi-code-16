# coding=utf-8

from django.http import HttpResponse
import json
import django

__author__ = 'Maple.Liu'


def response_as_json(request, obj, headers=dict(), before_response=None, ret_code_defines=None):
    """
    - 将一个Py对象转成JSON，构造返回HttpResponse
    - headers是由Http Header键值对组成的字典
    - before_response 是回调函数，发送响应数据之前要执行的操作
    - ret_code_defines 返回码的标注表

    def my_bofore_response(request):
        print request
        pass

    - response_as_json(request,
                        {'data':'test'},
                        headers={},
                        before_response=my_before_response,
                        ret_code_defines=ret_code_defines) => HttpResponse
    """
    if django.get_version() >= '1.6':
        response = HttpResponse(content_type="application/json")
    else:
        response = HttpResponse(mimetype='application/json')
    if 'code' in obj:
        import enum
        if type(ret_code_defines) == enum.EnumMeta:
            item = getattr(ret_code_defines, obj['code'], '')
            if item:
                obj['msg'] = item.value
        elif type(ret_code_defines) == dict:
            obj['msg'] = ret_code_defines.get(obj['code'], '')
    res = json.dumps(obj)
    response.write(res)
    if 'Access-Control-Allow-Origin' not in headers.keys():
        headers['Access-Control-Allow-Origin'] = '*'
    for k, v in headers.items():
        response[k] = v
    if before_response is not None:
        before_response(request)
    return response
