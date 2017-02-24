#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
from datetime import datetime

import pytz
from django.urls import reverse
from libs.payments.weixin.exceptions import WechatBaseException
from libs.payments.weixin.wxmp import WechatMpApi

from wcwxapi.core.request import WxpayRequest
from wcwxapi.core.response import WxpayResponse
from wcwxapi.core.utils import to_string, get_random_code

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


logger = logging.getLogger(__name__)




class WechatPayOrder(WeixinBaseParam):
    """
    微信订单对象
    """

    def __init__(self, account, body, detail, out_trade_no,
                 total_fee, spbill_create_ip,
                 time_start, time_expire, nonce_str=None,
                 goods_tag=None, device_info='WEB', trade_type='APP', attach=None, fee_type=None,
                 product_id=None, limit_pay=None, openid=None, sign_type='MD5'):
        super(WechatPayOrder, self).__init__(account)
        self.notify_url = getattr(settings, 'WEIXIN_PAY_V4_TRADE_NOTIFY_URL', None)
        self.body = to_string(body)
        self.detail = to_string(detail)
        self.out_trade_no = to_string(out_trade_no)
        self.total_fee = total_fee
        self.spbill_create_ip = spbill_create_ip
        self.time_start = time_start
        self.time_expire = time_expire
        self.trade_type = trade_type
        self.goods_tag = goods_tag
        self.device_info = device_info
        self.attach = attach
        self.fee_type = fee_type
        self.product_id = product_id
        self.limit_pay = limit_pay
        self.openid = openid
        self.nonce_str = nonce_str if nonce_str else get_random_code(32)
        self.sign_type = sign_type





class WechatPayApi(WechatBaseApi):
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

    def api_unifiedorder(self, param_obj):
        """
        统一下单
        :param param_obj: 下单的对象
        :return:
        """
        logger.debug('send post data to weixin server for unifiedorder')
        resource = '/pay/unifiedorder'
        resp = self.post(param_obj, resource, 'unifiedorder')
        return resp

    def get_client_pay_params(self, prepay_id, pay_type="APP"):
        """
        为客户端生成调起支付的参数
        注意, 微信支付 微信浏览器H5(WXH5) ,公众号(WXMP), App(APP)都不一样,
        :param prepay_id:
        :return:
        """

        # 给客户端准备数据
        noncestr = get_random_code(32)  # 随机码
        # 生成当前时间
        shtz = pytz.timezone('Asia/Shanghai')
        tz_now = datetime.now(tz=shtz)
        timestamp = int(time.mktime(tz_now.timetuple()))  # 时间戳

        params = {
            'appid': self._account.app_id,
            'signType': 'MD5',
            "timestamp": str(timestamp),
            'noncestr': noncestr,
        }

        if pay_type == "APP":
            params.update(
                {
                    'package': 'Sign=WXPay',
                    'prepayid': prepay_id,
                    'partnerid': self._account.mch_id,
                }
            )
            # 签名
            sign = self.get_request('/').sign(std_params=params)
            params.update({'sign': sign})
        elif pay_type == "WXMP" or pay_type == "WXH5":
            params = (
                {
                    'appId': self._account.app_id,
                    'signType': 'MD5',
                    "timeStamp": str(timestamp),
                    'nonceStr': noncestr,
                    'package': 'prepay_id=%s' % prepay_id,
                }
            )
            # 签名
            sign = self.get_request('/').sign(std_params=params)
            params.update({'paySign': sign})
        else:
            raise WechatBaseException('WechatError', 'the pay type param not correctly')
        logger.debug('the params for client pay')
        logger.debug(params)
        return params

    def wxmp_pay_order(self, wxmp_account, wx_order):
        """
        公众号下单支付, 获取页面需要的所有参数
        :param wx_order:
        :return:
        """
        result = self.api_unifiedorder(wx_order)
        content = result.content
        prepay_id = content['prepay_id']
        logger.debug(content)
        pay_params = self.get_client_pay_params(prepay_id, pay_type='WXMP')
        # 拿jsapi参数
        mp_api = WechatMpApi(wxmp_account)
        init_params = mp_api.get_jsapi_init_params(
            reverse('wxmp:wx-mp-pay-order'),
            "[\'chooseWXPay\']"
        )
        data = {
            "pay_params": pay_params,
            "config_params": init_params,
        }
        return data
