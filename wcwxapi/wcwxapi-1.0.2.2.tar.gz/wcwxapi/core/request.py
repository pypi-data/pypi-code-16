#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
请求包装
"""

import requests


class RequestParameters(object):
    """
    参数对象包装
    """

    def get_dict(self):
        """
        去掉空值
        :return:
        """
        to_dict = self.__dict__
        # 去除空值
        remove_none_value = dict((k, v) for k, v in to_dict.iteritems() if v)
        return remove_none_value


class WxBaseRequest:
    """
    基础请求包装类
    """

    def __init__(self,
                 host,
                 content_type="text/xml;charset=UTF-8",
                 headers=None,
                 scheme="http"):
        # 公共header
        if headers is None:
            headers = {}
        self.host = host
        # 默认的content type
        self.content_type = content_type
        self.headers = headers
        self.scheme = scheme

    def _get_resource(self, resource):
        url = "%s://%s%s" % (self.scheme, self.host, resource)
        return url

    def get(self, resource, params=None, headers=None):
        """
        发送get请求
        :return:
        """
        url = self._get_resource(resource)
        return requests.get(url, params=params, headers=headers)

    def post(self, resource, data, params=None, headers=None):
        """
        发送post请求
        :return:
        """
        url = self._get_resource(resource)
        return requests.post(url, data=data, params=params, headers=headers)

    def delete(self, resource, params=None, headers=None):
        """
        delete请求
        :return:
        """
        url = self._get_resource(resource)
        return requests.delete(url, params=params, headers=headers)
