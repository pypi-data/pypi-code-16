#!/usr/bin/python
# -*- coding: utf-8 -*-
from wcwxapi.core.encoding import force_text
from wcwxapi.core.models import WeixinBaseParam
from wcwxapi.core.utils import get_random_code

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


class WechatPayOrder(WeixinBaseParam):
    """
    微信订单对象
    """

    def __init__(self, appid, mch_id, body, detail, out_trade_no,
                 total_fee, spbill_create_ip,
                 notify_url,
                 time_start, time_expire, nonce_str=None,
                 goods_tag=None, device_info='WEB', trade_type='APP', attach=None, fee_type=None,
                 product_id=None, limit_pay=None, openid=None, sign_type='MD5'):
        self.appid = appid
        self.mch_id = mch_id
        self.body = force_text(body)
        self.detail = force_text(detail)
        self.out_trade_no = force_text(out_trade_no)
        self.total_fee = total_fee
        self.spbill_create_ip = spbill_create_ip
        self.time_start = time_start
        self.time_expire = time_expire
        self.trade_type = trade_type
        self.goods_tag = goods_tag
        self.notify_url = notify_url
        self.device_info = device_info
        self.attach = attach
        self.fee_type = fee_type
        self.product_id = product_id
        self.limit_pay = limit_pay
        self.openid = openid
        self.nonce_str = nonce_str if nonce_str else get_random_code(32)
        self.sign_type = sign_type


class WechatQueryOrder(WeixinBaseParam):
    """
    微信订单对象
    """

    def __init__(self, appid, mch_id, transaction_id=None, out_trade_no=None,
                 nonce_str=None, sign_type='MD5'):
        self.appid = appid
        self.mch_id = mch_id
        self.nonce_str = nonce_str if nonce_str else get_random_code(32)
        self.sign_type = sign_type
        self.transaction_id = transaction_id
        self.out_trade_no = out_trade_no

