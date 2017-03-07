# -*- coding: utf-8 -*-

import base64
import urllib2
import urllib
from sdk.config import Config


class OAuthClient:

    def __init__(self, app_key, secret, callback_url=None):
        self.client_id = app_key
        self.secret = secret
        self.callback_url = callback_url
        self.request_url = Config.get_access_token_url()
        self.authorize_url = Config.get_authorize_url()

    # 根据key和secret获取token（客户端授权模式）
    def get_token_in_client_credentials(self):
        data = {"grant_type": "client_credentials"}
        return self.do_request(data)

    # 构造授权URL（授权码模式）
    def get_auth_url(self, state, scope):
        url = self.authorize_url
        client_id = self.client_id
        response_type = "code"
        callback_url = urllib2.quote(self.callback_url)
        return "%s?response_type=%s&client_id=%s&state=%s&redirect_uri=%s&scope=%s" % (
            url, response_type, client_id, state, callback_url, scope)

    # 根据auth_code获取token（授权码模式）
    def get_token_by_auth_code(self, code):
        callback_url = self.callback_url
        data = {"grant_type": "authorization_code",
                "code": code,
                "redirect_uri": callback_url,
                "client_id": self.client_id}

        return self.do_request(data)

    # 根据refresh_token刷新获取token（授权码模式）
    def get_token_by_refresh_token(self, refresh_token, scope):
        data = {"grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": scope}

        return self.do_request(data)

    def do_request(self, body):
        req = urllib2.Request(self.request_url, urllib.urlencode(body).encode("ascii"),
                                     self.get_headers())
        response = urllib2.urlopen(req)
        result = response.read()
        return result.decode()

    def get_headers(self):
        slice = u"{}:{}".format(self.client_id, self.secret)
        value = base64.b64encode(bytes(slice))
        headers = {
            "Authorization": "Basic " + value.decode(),
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        return headers

