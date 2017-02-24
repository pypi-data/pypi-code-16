#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
微信支付的响应包装
"""
import logging

from requests import RequestException

from .exceptions import WechatBaseException, WechatApiErrorException
from .utils import xmlToArray

logger = logging.getLogger(__name__)


class WxBaseResponse(object):
    """
    处理完以后可以用data访问返回的内容
    """

    def __init__(self, business, resp):
        self.business = business
        self._resp = resp
        self.headers = resp.headers
        self.content = None

        if 'text/xml' in self.headers['content-type']:
            self.content_type = 'XML'
        elif 'json' in self.headers['content-type']:
            self.content_type = 'JSON'

        self._process()

    def _process(self):
        raise NotImplementedError


class WxDefaultResponse(WxBaseResponse):
    def _process(self):
        """
        处理数据
        :return:
        """
        # 数据类型
        if self.content_type == 'XML':
            self._proccess_xml()
        elif self.content_type == 'JSON':
            self._proccess_json()

    def _proccess_xml(self):
        try:
            status_code = self._resp.status_code
            if status_code != 200:
                logger.error('weixin pay status_code: %d , resp body: %s ' % (status_code, self._resp.text))
                raise WechatBaseException('WechatError', 'the server not return 200')
            self._resp.encoding = 'utf-8'
            xml_data = self._resp.text
            # 获取参数
            res_params = xmlToArray(xml_data)

            if res_params['return_code'] == 'SUCCESS':
                if res_params['result_code'] == 'SUCCESS':
                    self.content = res_params
                elif res_params['result_code'] == 'FAIL':
                    wx_error_code = res_params['err_code']
                    wx_error_msg = res_params['err_code_des']
                    logger.error(u'call weixin api error, code: %s', wx_error_code)
                    raise WechatApiErrorException('WechatError', wx_error_msg, wx_error_code)
            elif res_params['return_code'] == 'FAIL':
                wx_error_msg = res_params['return_msg']
                logger.error(u'call weixin api error: %s' % wx_error_msg)
                raise WechatBaseException('WechatError', wx_error_msg)
            else:
                raise WechatBaseException('WechatError', 'Unknown error')
        except RequestException as e:
            logger.exception(e)
            raise WechatBaseException('WechatError', 'request error')

    def _proccess_json(self):
        try:
            self._resp.encoding = 'utf-8'
            self.content = self._resp.json()
            if 'errcode' in self.content:
                error_code = self.content['errcode']
                if error_code != 0:
                    error_msg = self.content['errmsg']
                    logger.error(u'call weixin api error, code: %s', error_code)
                    raise WechatApiErrorException('WechatError', error_msg, error_code)
        except RequestException as e:
            logger.exception(e)
            raise WechatBaseException('WechatError', 'request error')