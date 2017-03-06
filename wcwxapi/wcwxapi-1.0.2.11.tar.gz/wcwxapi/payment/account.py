#!/usr/bin/python
# -*- coding: utf-8 -*-
from wcwxapi.core.account import Account


class WxPayAccount(Account):
    """
    账户配置信息
    """

    def __init__(self,
                 business, app_id, app_secret, mch_id):
        self.mch_id = mch_id
        super(WxPayAccount, self).__init__(business, app_id, app_secret)
