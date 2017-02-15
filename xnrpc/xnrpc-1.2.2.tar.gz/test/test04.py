#!/usr/bin/env python
# -*-coding:utf-8-*-
# 复杂一点的测试
# manager中有rpc server和多个thread
# rpc interface会调用manager中thread的方法

import unittest
from xnrpc.server import RpcInterface, ServerManager
from xnrpc.client import open_client
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


class OperationRpcInterface(RpcInterface):

    def ls_file(self):
        """两种调用方法"""
        _log.info('Operation ls file, now I call thread method')
        self._manager.opthread.work()
        return None

    def check_ip(self):
        """管道命令"""
        _log.info('Operation check ip, now I do nothing')
        return None


class OperationServerManager(ServerManager):
    def __init__(self, url, rpc_interface):
        super(OperationServerManager, self).__init__(
            url, rpc_interface, name='OperationServerManager')
        self.opthread = OperationThread(counter=100)

    def start(self):
        super(OperationServerManager, self).start()
        self.opthread.start()

    def stop(self):
        super(OperationServerManager, self).stop()
        self.opthread.stop()

    def join(self):
        super(OperationServerManager, self).join()
        self.opthread.join()


class RpcTest(unittest.TestCase):
    def test_server_manager(self):
        # 启动RPC服务器
        rpc_interface = OperationRpcInterface
        url = 'tcp://127.0.0.1:7779'
        server = OperationServerManager(url, rpc_interface)
        server.start()

        # 建立一个客户端连接
        with open_client(url) as client:
            client.ls_file()
            client.check_ip()

        # 停止服务器
        server.stop()


if __name__ == '__main__':
    unittest.main()