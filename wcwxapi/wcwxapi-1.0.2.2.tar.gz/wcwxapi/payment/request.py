#!/usr/bin/python
# -*- coding: utf-8 -*-
from wcwxapi.core.utils import arrayToXml

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


import collections
import hashlib
import logging

import requests

from wcwxapi.core.encoding import force_text

logger = logging.getLogger(__name__)


class WxpayRequest:
    """
    基础请求包装类
    """

    def __init__(self,
                 host,
                 ak_id,
                 ak_secret,
                 mch_id,
                 resource,
                 business,
                 content_type="text/xml;charset=UTF-8",
                 headers=None,
                 method="GET",
                 scheme="http"):
        if headers is None:
            headers = {}
        self.host = host
        self.ak_id = ak_id
        self.ak_secret = ak_secret
        self.mch_id = mch_id
        self.resource = resource
        self.business = business
        self.content_type = content_type
        self.headers = headers
        self.request_body = None
        self.method = method
        self.scheme = scheme
        # 判断是否build完成, 初始化为False
        self.built = False
        self.request_url = "%s://%s%s" % (self.scheme, self.host, self.resource)

    def sign(self, wx_param=None, std_params=None):
        """
        签名
        签名 参考 https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=4_3
        params          dict    参数
        :return:
        """
        prepare_params = {}
        if wx_param:
            prepare_params = self.prepare_params(wx_param)
        elif std_params:
            prepare_params = std_params
        sort_link_str = self.sort_link_params(prepare_params)

        # 拼接密钥
        prepare_str = '%s&key=%s' % (sort_link_str, self.ak_secret)
        prepare_str = force_text(prepare_str)
        logger.debug(prepare_str)
        # md5运算 然后转大写
        md5hash = hashlib.md5()
        md5hash.update(prepare_str)
        # 得到md5编码的字符串
        md5_str = md5hash.hexdigest()
        sign_str = md5_str.upper()
        return sign_str

    def prepare_params(self, wx_param):
        """
        为签名准备参数 整合商户参数 订单参数 随机码
        :param wx_param:
        :return:
        """
        prepare_params = wx_param.to_params()
        # prepare_params.update(self.params_mch)
        return prepare_params

    def sort_link_params(self, params):
        """
        排序参数,没有双引号,支付宝的有双引号, 这是第一步
        :param params:
        :return:
        """
        linked_string = ''
        p_copy = params.copy()
        if p_copy.has_key('sign'):
            p_copy.pop('sign')
        # 排序参数
        sorted_d = collections.OrderedDict(sorted(p_copy.items()))
        logger.debug(sorted_d)
        for k, v in sorted_d.iteritems():
            v = force_text(v)
            linked_string = '%s&%s=%s' % (linked_string, k, v)
        linked_string = linked_string[1:]
        logger.debug('get weixin pay sort link string: [%s]' % linked_string)
        return linked_string

    def build_xml_body(self, wx_order_param):
        """
        第三步 加上签名 生成请求的xml数据
        :param wx_order_param:
        :return:
        """
        """
        :param wx_order_param:
        :return:
        """
        sign = self.sign(wx_order_param)
        params_without_sign = self.prepare_params(wx_order_param)
        params_without_sign.update({'sign': sign})
        xml_data = arrayToXml(params_without_sign)
        return xml_data

    def post(self, data):
        """
        发送post请求
        :return:
        """
        self.method = "POST"
        post_data = self.build_xml_body(data)
        logger.debug(post_data)
        self.request_body = post_data
        return requests.post(self.request_url, headers=self.headers, data=post_data)

    def get(self):
        """
        发送get请求
        :return:
        """
        self.method = "GET"
        return requests.get(self.request_url, headers=self.headers)

    def delete(self):
        """
        delete请求
        :return:
        """
        self.method = "DELETE"
        return requests.delete(self.request_url, headers=self.headers)