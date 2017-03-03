#!/usr/bin/python
# -*- coding: utf-8 -*-
import collections
import hashlib

from wcwxapi.core.encoding import force_text, force_bytes
from .six import iteritems


def sort_link_params(params):
    """
    链接并排序参数 参数为字典
    :return:
    """
    linked_string = ''
    p_copy = params.copy()
    if 'sign' in p_copy:
        p_copy.pop('sign')
    # 排序参数
    sorted_d = collections.OrderedDict(sorted(p_copy.items()))
    for (k, v) in iteritems(sorted_d):
        v = force_text(v)
        linked_string = '%s&%s=%s' % (linked_string, k, v)
    linked_string = linked_string[1:]
    return linked_string


def sign(params, api_secret):
    """
    签名算法
    :return:
    """
    """
    签名
    签名 参考 https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=4_3
    params          dict    参数
    :return:
    """
    sort_link_str = sort_link_params(params)

    # 拼接密钥
    prepare_str = '%s&key=%s' % (sort_link_str, api_secret)
    prepare_str = force_text(prepare_str)
    # md5运算 然后转大写
    md5hash = hashlib.md5()
    md5hash.update(force_bytes(prepare_str))
    # 得到md5编码的字符串
    md5_str = md5hash.hexdigest()
    sign_str = md5_str.upper()
    return sign_str


def mp_sign(params):
    linked_string = ''
    p_copy = params.copy()
    if p_copy.has_key('sign'):
        p_copy.pop('sign')
    # 排序参数
    sorted_d = collections.OrderedDict(sorted(p_copy.items()))
    for (k, v) in iteritems(sorted_d):
        v = force_bytes(v)
        # if isinstance(v, unicode):
        #     v = v.encode('utf-8')
        linked_string = '%s&%s=%s' % (linked_string, k, v)
    linked_string = linked_string[1:]
    # 签名
    sha = hashlib.sha1(linked_string)
    sign = sha.hexdigest()
    return sign
