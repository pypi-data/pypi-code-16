# coding:utf-8
'''
Created on 2017.1.2

@author: shenlang
'''
from Validator import validator
import requests
import json

class Http(object):
    def __init__(self):
        pass
    '''
    
    功能描述 用于HTTP接口调用和检查
    
    依赖库：
    + requests
    '''
    
    def request(self, url, method='GET', json_format=True, **kwargs):
        biz, verify = validator.filter_param(**kwargs)
        print biz
        if method == 'GET':
            response = requests.get(url, biz)
        else:
            response = requests.post(url, biz)
        print response.url
        response.raise_for_status()
        if json_format:
            result = response.json()
            print json.dumps(result, indent=4, ensure_ascii=False)
            validator.validate(result, **verify)
        else:
            result = response.text
        return result
    
    
    def simpleRequest(self, url, method='GET', json_format=True):
        if method == 'GET':
            response = requests.get(url)
        else:
            response = requests.post(url)
        print response.url
        response.raise_for_status()
        if json_format:
            result = response.json()
            print json.dumps(result, indent=4, ensure_ascii=False)
            validator.validate(result)
        else:
            result = response.text
        return result
    
    
    
    
    
    def get(self, url, json=True, **kwargs):
        '''
        功能：
        - http GET请求。
        
        参数：
        - url 请求地址
        - json 服务端返回结果类型，默认为json
        - **kwargs 业务参数和校验参数，校验参数以下划线开头，详见validator文档
            
        返回值：
        - http请求返回结果，若json=True则为字典类型，否则返回字符串
    
        例子：
        | get | ${some_url} | version=123 | device_model=MagicBox2 | _code='200' | _data__len=7 | _data_0_id='38' | _data_0_id__gte=38 |
        '''
        if len(kwargs) == 0:
            return self.simpleRequest(url, method='GET', json_format=json)
        
        return self.request(url, method='GET', json_format=json, **kwargs)
    
    def post(self, url, json=True, **kwargs):
        '''
        功能：
        - http POST请求。
        
        参数：
        - url 请求地址
        - json 服务端返回结果类型，默认为json
        - **kwargs 业务参数和校验参数，校验参数以下划线开头，详见validator文档
            
        返回值：
        - http请求返回结果，若json=True则为字典类型，否则返回字符串
    
        例子：
        | post | ${some_url} | version=123 | device_model=MagicBox2 | _code='200' | _data__len=7 | _data_0_id='38' | _data_0_id__gte=38 |
        '''
        return self.request(url, method='POST', json_format=json, **kwargs)
    
if __name__ == '__main__':
    http = Http()
#     url = 'http://video.alitv.yunos.com/v4/video/home/item/'
#     print http.get(url, system_info='{"device_model": "MagicBox2", "version_code": "2100202108", "uuid": "7D95B84DE9F2F6C3A7D198C8F56DAB55"}',
#                    _code='200', _message='SUCCESS', _success='true',
#                    _data__len=7, _data_0_id='38', _data_0_extra__len_gte=1,
#                    _data_0_id__gte=38, _data_0_id__lte=38,
#                    _data_0_id__gt=37, _data_0_id__lt=39)
    http.get('http://www.weather.com.cn/data/sk/101010100.html', json)
    
    