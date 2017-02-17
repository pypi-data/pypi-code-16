#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
公众号相关接口
"""
import collections
import hashlib
import time
from datetime import datetime

import pytz
import requests
from libs.redis.connection import RedisConnection
from ttdashi import settings

from wcwxapi.core.request import WxpayRequest
from .pay import WechatBaseApi
from .utils import get_random_code

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"

redis_conn = RedisConnection()
cache_wxmp_key = 'WECHAT_CACHE'
cache_access_key = 'ACCESS_TOKEN'
JSAPI_TICKET = "JSAPI_TICKET"


class WechatMpApi(WechatBaseApi):
    def get_request(self, resource):
        request = WxpayRequest(
            host=self._host,
            ak_id=self._account.app_id,
            ak_secret=self._account.app_secret,
            mch_id=self._account.mch_id,
            resource=resource,
            business=self._business,
            method="POST",
            scheme="https"
        )
        return request

    def get_wxmp_token(self):
        """
        get wechat mp access_token, this token is not user access_token
        :return:
        """
        # get from the cache first
        wx_cache = redis_conn().hgetall(cache_wxmp_key)
        access_token = None
        if wx_cache:
            access_token = redis_conn().hget(cache_wxmp_key, cache_access_key)
        if not access_token:
            access_token_url = getattr(settings, "WECHAT_MP_COMMON_ACCESS_TOKEN_URL", None)
            resp = requests.get(access_token_url)
            resp.encoding = 'utf-8'
            content = resp.json()
            if content.has_key('access_token'):
                # 缓存
                access_token = content['access_token']
                redis_conn().hset(
                    cache_wxmp_key, cache_access_key, access_token)
                redis_conn().expire(cache_wxmp_key, 7180)
        return access_token

    def get_ticket(self):
        """
        获取jsapi的 ticket
        :return:
        """
        access_token = self.get_wxmp_token()
        wx_cache = redis_conn().hgetall(cache_wxmp_key)
        ticket = None
        if wx_cache :
            ticket = redis_conn().hget(cache_wxmp_key, JSAPI_TICKET)
        if not ticket:
            if isinstance(access_token, unicode):
                access_token = access_token.encode('utf-8')
            ticket_url = getattr(settings, "WECHAT_API_JSAPI_TICKET_URL", None) % access_token
            resp = requests.get(ticket_url)
            resp.encoding = 'utf-8'
            content = resp.json()
            if content.has_key('ticket'):
                ticket = content['ticket']
                redis_conn().hset(
                    cache_wxmp_key, JSAPI_TICKET, ticket)
                redis_conn().expire(JSAPI_TICKET, 7180)
        return ticket

    def get_jsapi_init_params(self, url, api_list):
        """
        生成客户端 jsapi的基础参数, 签完名后,将所有参数返回给客户端
        """


        # 给客户端准备数据
        noncestr = get_random_code(32)  # 随机码
        # 生成当前时间
        shtz = pytz.timezone('Asia/Shanghai')
        tz_now = datetime.now(tz=shtz)
        timestamp = int(time.mktime(tz_now.timetuple()))  # 时间戳

        jsapi_ticket = self.get_ticket()
        # 待签名参数
        params = {
            "url": url,
            "jsapi_ticket": jsapi_ticket,
            "timestamp": str(timestamp),
            'noncestr': noncestr,
        }

        linked_string = ''
        p_copy = params.copy()
        if p_copy.has_key('sign'):
            p_copy.pop('sign')
        # 排序参数
        sorted_d = collections.OrderedDict(sorted(p_copy.items()))
        for k, v in sorted_d.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            linked_string = '%s&%s=%s' % (linked_string, k, v)
        linked_string = linked_string[1:]
        # 签名
        sha = hashlib.sha1(linked_string)
        sign = sha.hexdigest()

        params.update(
            {
                'appid': self._account.app_id,
                'signature': sign,
                'jsApiList': api_list,
            }
        )
        return params



