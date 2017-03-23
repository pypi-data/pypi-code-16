#!usr/bin/env python
# coding:utf-8

import logging
from threading import Thread
from .messages import Registered,Message,MessageConfig

logger = logging.getLogger(__name__)

class YBAI(object):

    def __init__(self):
        print('初始化AI')

        self.setup()
        pass

    def setup(self):
        print('设置配置')
        self.reg = Registered(self)
        pass

    @property
    def receiveMsgHandle(self, msg):

        conf = self.reg.getConfig(msg)
        print(conf)
        if not conf:
            return
        def process():
            try:
               res = conf.func(msg)
               if res:
                   print('又返回结果')
            except:
                print('异常发送')
        Thread(target=process, daemon=True).start()


    def register(self,except_self = None):
        def do_register(func):
            self.reg.append(MessageConfig(ai=self,func=func,except_self=except_self))
            print('收到注册消息')
            return func
            pass
        print('注册事件')
        return do_register
        pass

    def start(self):
        print('开始')
        """
        开始消息监听和处理 (登陆后会自动开始)
        """
        pass

    def stop(self):
        print('stop')
        """
        停止消息监听和处理 (登出后会自动停止)
        """
        pass

    def _cleanup(self):
        print('清空')
        pass