#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


class Account(object):
    """
    账户配置信息
    """

    def __init__(self,
                 business, app_id, app_secret):
        """
        业务名称 比如 PAY,WXMP,WXOPEN 对应微信支付, 微信公众号开发, 微信开放平台
        :param business:
        """
        self.business = business
        self.app_id = app_id
        self.app_secret = app_secret



