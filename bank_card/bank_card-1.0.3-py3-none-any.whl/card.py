#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: contactxjw@gmail.com
# Created at 2016-12-07

from __future__ import absolute_import, unicode_literals

import json

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from .static import *


class BankCard(object):
    def __init__(self, card_num=None):
        self.card_num = card_num
        self.__info(card_num)

    def __info(self, card_num):
        result = json.loads(
            urlopen('https://ccdcapi.alipay.com/validateAndCacheCardInfo.json'
                    '?_input_charset=utf-8&cardNo={}&cardBinCheck=true'
                    .format(card_num)
                    )
            .read()
            .decode('utf-8')
        )

        if not result['validated']:
            self.validated = False
        else:
            self.validated = True
            self.bank = result['bank']
            self.bank_name = BANK_INFO.get(self.bank)
            self.bank_image = 'https://apimg.alipay.com/combo.png?d=cashier&t=%s' % self.bank
            self.card_type = result['cardType']
            self.card_type_name = CARD_TYPE.get(self.card_type)

    def to_dict(self):
        if self.validated:
            return {
                'validated': True,
                'bank': self.bank,
                'bank_name': self.bank_name,
                'bank_image': self.bank_image,
                'card_type': self.card_type,
                'card_type_name': self.card_type_name,
            }
        else:
            return {
                'validated': False,
            }
