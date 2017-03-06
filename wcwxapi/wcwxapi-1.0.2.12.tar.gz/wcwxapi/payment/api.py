#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
from datetime import datetime

import pytz

from wcwxapi.core.api import WechatBaseApi
from wcwxapi.core.encoding import force_text
from wcwxapi.core.exceptions import WechatBaseException, WechatApiErrorException
from wcwxapi.core.request import WxBaseRequest
from wcwxapi.core.signature import sign as wxpay_signature
from wcwxapi.core.utils import get_random_code, arrayToXml, xmlToArray

logger = logging.getLogger(__name__)


class WechatPayApi(WechatBaseApi):
    """
    微信公众号api
    """
    API_HOST = 'api.mch.weixin.qq.com'

    def __init__(self, account, response_class=None, redis_connection=None):
        assert redis_connection, 'you must use redis cache'
        self.redis_connection = redis_connection
        business = 'WechatPay'

        self.request = WxBaseRequest(
            host=self.API_HOST,
            scheme="https"
        )
        super(WechatPayApi, self).__init__(account, response_class, business)

    def get_request(self):

        return self.request

    def _prepare_params(self, wx_param):
        """
        为签名准备参数 整合商户参数 订单参数 随机码
        :param wx_param:
        :return:
        """
        prepare_params = wx_param.to_params()
        # prepare_params.update(self.params_mch)
        return prepare_params

    def _build_xml_body(self, wx_order_param):
        """
        第三步 加上签名 生成请求的xml数据
        :param wx_order_param:
        :return:
        """
        """
        :param wx_order_param:
        :return:
        """
        sign = wxpay_signature(wx_order_param.to_params(), self._account.app_secret)
        params_without_sign = self._prepare_params(wx_order_param)
        params_without_sign.update({'sign': sign})
        xml_data = arrayToXml(params_without_sign)
        return xml_data

    def api_unifiedorder(self, param_obj):
        """
        统一下单
        :param param_obj: 下单的对象
        :return:
        """
        logger.debug('send post data to weixin server for unifiedorder')
        resource = '/pay/unifiedorder'
        # 对象转成dict

        post_data = self._build_xml_body(param_obj)
        logger.debug(post_data)
        resp = self.post(resource, force_text(post_data))

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
            sign = wxpay_signature(params, self._account.app_secret)
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
            sign = wxpay_signature(params, self._account.app_secret)
            params.update({'paySign': sign})
        else:
            raise WechatBaseException('WechatError', 'the pay type param not correctly')
        logger.debug('the params for client pay')
        logger.debug(params)
        return params

    def get_notify_results_dict(self, data):
        """
        处理微信的支付结果,转成dict
        :param data:
        :return:
        """
        # 先要验证签名
        params = xmlToArray(data.decode('utf-8'))

        if self._verify_weixin_sign(params):
            # 验证成功
            logger.debug("verify weixin notify callback success!")
            if params['return_code'] == 'SUCCESS':
                if params['result_code'] == 'SUCCESS':
                    pass
                elif params['result_code'] == 'FAIL':
                    wx_error_code = params['err_code']
                    wx_error_msg = params['err_code_des']
                    logger.error(u'weixin callback error, code: %s', wx_error_code)
                    raise WechatApiErrorException('WechatError', wx_error_msg, wx_error_code)
            elif params['return_code'] == 'FAIL':
                wx_error_msg = params['return_msg']
                logger.error(u'weixin callback error: %s' % wx_error_msg)
                raise WechatBaseException('WechatError', wx_error_msg)
            else:
                raise WechatBaseException('WechatError', 'Unknown error')

        return params

    def _verify_weixin_sign(self, params):
        """
        验证回调的签名
        :param params:
        :return:
        """
        sign = params.get('sign')
        cal_sign = wxpay_signature(params, self._account.app_secret)
        return True if sign == cal_sign else False

    def api_query_order(self, query_obj):
        resource = '/pay/orderquery'
        # 对象转成dict

        post_data = self._build_xml_body(query_obj)
        logger.debug(post_data)
        resp = self.post(resource, force_text(post_data))
        return resp










        # def wxmp_pay_order(self, wxmp_account, wx_order):
        #     """
        #     公众号下单支付, 获取页面需要的所有参数
        #     :param wx_order:
        #     :return:
        #     """
        #     result = self.api_unifiedorder(wx_order)
        #     content = result.content
        #     prepay_id = content['prepay_id']
        #     logger.debug(content)
        #     pay_params = self.get_client_pay_params(prepay_id, pay_type='WXMP')
        #     # 拿jsapi参数
        #     mp_api = WechatMpApi(wxmp_account)
        #     init_params = mp_api.get_jsapi_init_params(
        #         reverse('wxmp:wx-mp-pay-order'),
        #         "[\'chooseWXPay\']"
        #     )
        #     data = {
        #         "pay_params": pay_params,
        #         "config_params": init_params,
        #     }
        #     return data
