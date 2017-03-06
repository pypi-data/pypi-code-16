#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections
import hashlib
import time
from datetime import datetime

import pytz

from wcwxapi.core.encoding import force_bytes, force_text
from wcwxapi.core.request import WxBaseRequest
from ..core.api import WechatBaseApi
from ..core.utils import get_random_code


class WechatMpApi(WechatBaseApi):
    """
    微信公众号api
    """
    WECHAT_MP_CACHE_KEY = 'WECHAT_MP_CACHE'
    CLIENT_ACCESS_TOKEN_CACHE_KEY = 'CLIENT_ACCESS_TOKEN'
    JSAPI_TICKET_CACHE_KEY = "JSAPI_TICKET"

    API_HOST = 'api.weixin.qq.com'

    def __init__(self, account, response_class=None, redis_connection=None):
        assert redis_connection, 'you must use redis cache'
        self.redis_connection = redis_connection
        business = 'WechatMp'
        super(WechatMpApi, self).__init__(account, response_class, business)

    def get_request(self):
        request = WxBaseRequest(
            host=self.API_HOST,
            scheme="https"
        )
        return request

    def fetch_client_access_token(self):
        """
        获取客户端token, 此token并非用户token, 每日限额2000, 7200秒后过期
        :return:
        """
        access_token = None
        wxmp_cache = self.redis_connection.hgetall(self.WECHAT_MP_CACHE_KEY)
        if wxmp_cache:
            access_token = self.redis_connection.hget(self.WECHAT_MP_CACHE_KEY,
                                                      self.CLIENT_ACCESS_TOKEN_CACHE_KEY)
        if not access_token:
            params = {
                'grant_type': 'client_credential',
                'appid': self._account.app_id,
                'secret': self._account.app_secret,
            }

            resp = self.get('/cgi-bin/token', params=params)
            content = resp.content
            if 'access_token' in content:
                # 缓存
                access_token = force_text(content['access_token'])
                self.redis_connection.hset(
                    self.WECHAT_MP_CACHE_KEY, self.WECHAT_MP_CACHE_KEY, access_token)
                self.redis_connection.expire(self.WECHAT_MP_CACHE_KEY, 7180)
        return access_token

    def get_jsapi_ticket(self):
        """
        获取jsapi的 ticket
        :return:
        """
        access_token = self.fetch_client_access_token()
        wx_cache = self.redis_connection.hgetall(self.WECHAT_MP_CACHE_KEY)
        ticket = None
        if wx_cache:
            ticket = self.redis_connection.hget(self.WECHAT_MP_CACHE_KEY, self.JSAPI_TICKET_CACHE_KEY)
        if not ticket:
            access_token = force_bytes(access_token)
            # if isinstance(access_token, unicode):
            #     access_token = access_token.encode('utf-8')
            params = {
                'access_token': access_token,
                'type': 'jsapi',
            }
            resp = self.get('/cgi-bin/ticket/getticket', params=params)
            content = resp.content
            if 'ticket' in content:
                ticket = force_text(content['ticket'])
                self.redis_connection.hset(
                    self.WECHAT_MP_CACHE_KEY, self.JSAPI_TICKET_CACHE_KEY, ticket)
                self.redis_connection.expire(self.JSAPI_TICKET_CACHE_KEY, 7180)
        return ticket

    def get_jsapi_signature(self, url, api_list):
        """
        生成客户端 jsapi的基础参数, 签完名后,将所有参数返回给客户端
        """

        # 给客户端准备数据
        noncestr = get_random_code(32)  # 随机码
        # 生成当前时间
        shtz = pytz.timezone('Asia/Shanghai')
        tz_now = datetime.now(tz=shtz)
        timestamp = int(time.mktime(tz_now.timetuple()))  # 时间戳

        jsapi_ticket = self.get_jsapi_ticket()
        # 待签名参数
        params = {
            "url": url,
            "jsapi_ticket": jsapi_ticket,
            "timestamp": str(timestamp),
            'noncestr': noncestr,
        }

        linked_string = ''
        p_copy = params.copy()
        if 'sign' in p_copy:
            p_copy.pop('sign')
        # 排序参数
        sorted_d = collections.OrderedDict(sorted(p_copy.items()))
        for k in sorted_d:
            v = sorted_d[k]
            # v = sorted_d[k]
            # if isinstance(v, unicode):
            #     v = v.encode('utf-8')
            linked_string = u'%s&%s=%s' % (force_text(linked_string), force_text(k), force_text(v))
        linked_string = linked_string[1:]
        # 签名
        sha = hashlib.sha1(force_bytes(linked_string))
        sign = sha.hexdigest()

        params.update(
            {
                'appid': self._account.app_id,
                'signature': sign,
                'jsApiList': api_list,
            }
        )
        return params
