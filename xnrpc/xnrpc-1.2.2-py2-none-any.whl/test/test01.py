#!/usr/bin/env python
# -*-coding:utf-8-*-
# 测验gevent协程

import unittest
from xnrpc.common.thread import ServerThread
from xnrpc.common.log import get_log
_log = get_log(__name__)


class OperationThread(ServerThread):

    def __init__(self, counter = 1):
        super(OperationThread, self).__init__()
        self.counter = counter

    def work(self):
        _log.info('OperationThread, counter={}'.format(self.counter))
        _log.info('OperationThread, counter={}'.format(self.counter + 1))
        _log.info('OperationThread, counter={}'.format(self.counter + 2))


class ThreadTest(unittest.TestCase):
    def test_operation_thread(self):
        t = OperationThread(counter=3)
        t.start()

        import time
        time.sleep(3)

        # now stop thread
        t.stop()

