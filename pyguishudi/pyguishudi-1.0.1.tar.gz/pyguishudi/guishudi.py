# -*- coding:utf-8 -*-

from pyguishudi.model.phone_prefix import PhonePrefix

def search(phone):
    """ 根据手机号，获得手机归属
    """
    return PhonePrefix.search(phone=phone)