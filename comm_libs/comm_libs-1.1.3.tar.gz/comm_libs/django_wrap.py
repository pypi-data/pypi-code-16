# coding:utf8

# 这里存放对django库的二次封装的相关代码
import json

from django.http import HttpResponse


class HzfHttpResponse(HttpResponse):
    """
    hzf http响应对象，所有view函数均需要返回此对象
    """

    def __init__(self, value):
        '''
        功能：value为参数字典
        '''

        if type(value) != dict:
            raise KeyError('param value must be a dict.')

        super(HzfHttpResponse, self).__init__()
        self.value = value


def gen_hzf_http_rsp(code, desc, value):
    """
    生成特定格式返回
    """

    if type(value) != dict:
        raise KeyError('param value must be a dict')

    output_template = {
        "status":
            {
                "code": "0",
                "description": "success"
            },
        "result":
            {

            }
    }

    output_template["status"]["code"] = code
    output_template["status"]["description"] = desc
    output_template["result"] = value

    res = HttpResponse()

    json_str = json.dumps(output_template, ensure_ascii=False)

    res.content = json_str

    res['Content-Type'] = 'application/json; charset=utf-8'

    return res


def get_request_value(request, key, default_val=""):
    """
    获取客户端参数
    :param request:
    :param key: 参数
    :param default_val: 默认值
    :return:
    """
    if not request.REQUEST.get(key):
        return default_val
    return request.REQUEST.get(key, default_val).strip()


def get_request_cookies(request, key, default_val=""):
    """
    获取客户端参数
    :param request:
    :param key: 参数
    :param default_val: 默认值
    :return:
    """
    if not request.COOKIES.get(key):
        return default_val
    return request.COOKIES.get(key, default_val).strip()


def get_dict_value(data_dict, key, default_val=""):
    if not data_dict.get(key):
        return default_val
    return data_dict.get(key, default_val).strip()
