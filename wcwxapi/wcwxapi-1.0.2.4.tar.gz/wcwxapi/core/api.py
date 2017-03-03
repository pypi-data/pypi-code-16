#!/usr/bin/python
# -*- coding: utf-8 -*-
from wcwxapi.core.response import WxDefaultResponse

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


class WechatBaseApi(object):
    def __init__(self, account, response_class=None, business=None):
        self._account = account
        self._business = business
        if not response_class:
            self.response_class = WxDefaultResponse
        else:
            self.response_class = response_class

    def get_request(self):
        raise NotImplementedError

    def post(self, resource, data, params=None, headers=None):
        req = self.get_request()
        resp = req.post(resource, data, params, headers)
        wx_resp = self.response_class(self._business, resp)
        return wx_resp

    def get(self, resource, params=None, headers=None):
        req = self.get_request()
        resp = req.get(resource, params, headers)
        wx_resp = self.response_class(self._business, resp)
        return wx_resp

    def delete(self, resource, params=None, headers=None):
        req = self.get_request()
        resp = req.delete(resource, params, headers)
        wx_resp = self.response_class(self._business, resp)
        return wx_resp
