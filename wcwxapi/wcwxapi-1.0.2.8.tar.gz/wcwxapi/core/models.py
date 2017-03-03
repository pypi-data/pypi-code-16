#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)


class WeixinBaseParam(object):
    """
    参数对象包装
    """

    def to_params(self):
        to_dict = self.__dict__
        # 去除空值
        if PY3:
            remove_none_value = {k: v for k, v in to_dict.items() if v is not None}
        elif PY2:
            remove_none_value = dict((k, v) for k, v in to_dict.iteritems() if v)
        return remove_none_value
