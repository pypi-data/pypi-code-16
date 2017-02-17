#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
微信支付的响应包装
"""
import logging

from requests import RequestException

from .utils import xmlToArray
from .exceptions import WechatBaseException, WechatApiErrorException

logger = logging.getLogger(__name__)

class WxpayResponse(object):
    def __init__(self, business, resp):
        self.business = business
        self._resp = resp
        self.headers = resp.headers

        self._process()

    def _process(self):
        """
        处理数据
        :return:
        """
        # 数据类型
        try:

            status_code = self._resp.status_code
            if status_code != 200:
                logger.error('weixin pay status_code: %d , resp body: %s ' % (status_code, self._resp.text))
                raise WechatBaseException('WechatError', 'the server not return 200')
            self._resp.encoding = 'utf-8'
            xml_data = self._resp.text

            # 获取参数
            res_params = xmlToArray(xml_data)
            logger.debug(res_params)

            if res_params['return_code'] == 'SUCCESS':
                if res_params['result_code'] == 'SUCCESS':
                    self.content = res_params
                    return None
                elif res_params['result_code'] == 'FAIL':
                    wx_error_code = res_params['err_code']
                    wx_error_msg = res_params['err_code_des']
                    logger.error(u'weixin pay error, code: %s', wx_error_code)
                    raise WechatApiErrorException('WechatError', wx_error_msg, wx_error_code)
            elif res_params['return_code'] == 'FAIL':
                wx_error_msg = res_params['return_msg']
                logger.error(u'weixin pay error: %s' % wx_error_msg)
                raise WechatBaseException('WechatError', wx_error_msg)
            else:
                raise WechatBaseException('WechatError', 'Unknown error')
        except RequestException as e:
            logger.exception(e)
            raise WechatBaseException('WechatError', 'request error')