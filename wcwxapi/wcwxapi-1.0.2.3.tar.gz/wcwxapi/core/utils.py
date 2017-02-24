#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import string
import xml.etree.ElementTree as ET
from datetime import timedelta, datetime

import pytz

from .encoding import force_text

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


def get_random_code(code_length=10):
    """
    获取随机码
    """
    assert 4 <= code_length <= 32, "the length must more than 4, and less than 32"
    random_code_string = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(code_length))
    return random_code_string


def get_random_number(code_length=6):
    assert 4 <= code_length <= 32, "the length must more than 4, and less than 32"
    random_number_string = ''
    # chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    chars = '0123456789'
    length = len(chars) - 1
    random_obj = random.Random()
    for i in range(code_length):
        random_number_string += chars[random_obj.randint(0, length)]
    return random_number_string


def to_string(src_str):
    if isinstance(src_str, str):
        return src_str
    elif isinstance(src_str, unicode):
        return src_str.encode('utf-8')


def arrayToXml(arr):
    """array转xml"""
    xml = [u"<xml>"]
    for k, v in arr.iteritems():
        if isinstance(v, int) or isinstance(v, float):
            xml.append(u"<{0}>{1}</{0}>".format(k, v))
        elif v.isdigit():
            xml.append(u"<{0}>{1}</{0}>".format(k, v))
        else:
            text_v = force_text(v)
            xml.append(u"<{0}><![CDATA[{1}]]></{0}>".format(k, text_v))
    xml.append(u"</xml>")
    xml_body = u"".join(xml)
    xml_body_utf8 = xml_body.encode('utf-8')
    return xml_body_utf8


def xmlToArray(xml):
    """将xml转为array"""
    array_data = {}
    root = ET.fromstring(xml.encode('utf-8'))
    for child in root:
        value = child.text
        if value:
            array_data[child.tag] = value
    return array_data


def get_pay_time():

    shtz = pytz.timezone('Asia/Shanghai')
    tz_now = datetime.now(tz=shtz)
    # 交易开始时间
    time_start = tz_now.strftime('%Y%m%d%H%M%S')
    # 交易结束时间 指定时间之后
    td = timedelta(minutes=10)
    tz_pay_expire = tz_now + td
    time_expire = tz_pay_expire.strftime('%Y%m%d%H%M%S')
    time_dict = {
        'time_start': time_start,
        'time_expire': time_expire
    }
    return time_dict
