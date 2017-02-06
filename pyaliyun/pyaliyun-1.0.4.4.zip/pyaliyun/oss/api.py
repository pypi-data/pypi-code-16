#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
参考: https://help.aliyun.com/product/31815.html?spm=5176.doc31935.3.1.wb3Fy5
"""
import base64
import time
from datetime import timedelta, datetime
from time import gmtime

from pyaliyun.core.api import BaseApi


class Helper(BaseApi):
    """
    some useful api tools
    """

    def __init__(self, host, account, schema="https", service="OSS"):
        self._host = host
        self._schema = schema
        self._endpoint = "%s://%s" % (self._schema, self._host)
        self._header_prefix = "x-oss-"
        super(Helper, self).__init__(account, service)

    def get_policy(self, size=10):
        """
            表单提交到oss的方法需要能获取一个policy的编码数据
            这里将过期时间延后一个小时
            """
        # 获取gmt时间
        gmt_struct = gmtime()
        # struct 转化成time对象
        gmt_time = time.mktime(gmt_struct)
        # 转datetime
        gmt_dt = datetime.fromtimestamp(gmt_time)
        # 获取 开始后的10分钟, 10分钟后过期
        timeout_delta = timedelta(minutes=10)
        policy_gmt_dt = gmt_dt + timeout_delta
        # 组成json字符串
        policy_gmttime = policy_gmt_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        file_size = 1024 * 1024 * size
        policy_json = '{"expiration": "%s","conditions": [["content-length-range"' \
                      ', 0, %d]]}' % (policy_gmttime, file_size)
        # % gmt_time
        # 转化utf8
        policy_json_utf8 = convert_utf8(policy_json)
        # 进行base64编码
        policy_value = base64.standard_b64encode(policy_json_utf8).strip()
        return policy_value

def convert_utf8(input_string):
    """
    utf8编码
    """
    if isinstance(input_string, unicode):
        input_string = input_string.encode('utf-8')
    return input_string
