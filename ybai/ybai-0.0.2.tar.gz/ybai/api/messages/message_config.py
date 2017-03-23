#!usr/bin/env python
# coding:utf-8

class MessageConfig(object):

    def __init__(self, ai, func, except_self):
        self.ai = ai
        self.func = func
        self.except_self = except_self
        print('消息配置')