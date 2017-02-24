#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


class WechatBaseException(Exception):
    """
    基础异常类
    """

    def __init__(self, error_type, message):
        self.error_type = error_type
        self.message = message

    def get_error_info(self):
        return "(\"%s\" \"%s\")\n" % (self.error_type, self.message)

    def __str__(self):
        return "ServiceException  %s" % (self.get_error_info())


class WechatApiErrorException(WechatBaseException):
    def __init__(self, error_type, message, error_code=None):
        self.error_code = error_code
        super(WechatApiErrorException, self).__init__(error_type, message)

    def get_error_info(self):
        return "(\"%s\" \"%s\")\n Param name : %s" % \
               (self.error_type, self.message, self.error_code)

    def __str__(self):
        return "ErrorCodeException  %s" % (self.get_error_info())


class WechatParamErrorException(WechatApiErrorException):
    def __init__(self, error_type, message, error_code=None, param_name=None):
        self.param_name = param_name
        super(WechatParamErrorException, self).__init__(error_type, message, error_code)

    def get_error_info(self):
        return "(\"%s\" \"%s\")\n, error code: %s , Param name : %s" % \
               (self.error_type, self.message, self.error_code, self.param_name)

    def __str__(self):
        return "ParamErrorException  %s" % (self.get_error_info())
