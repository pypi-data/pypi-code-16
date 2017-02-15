#!/usr/bin/env python
# -*-coding:utf-8-*-
# 测验正常的rpc服务器

import unittest
from xnrpc.server import RpcInterface, ServerManager
from xnrpc.client import open_client
from xnrpc.common.log import get_log
_log = get_log(__name__)


class OperationRpcInterface(RpcInterface):

    def ls_file(self):
        _log.info('Operation ls file')
        return None

    def check_ip(self):
        _log.info('Operation check ip')
        return None


class RpcTest(unittest.TestCase):
    def test_server_manager(self):
        # 启动RPC服务器
        rpc_interface = OperationRpcInterface
        url = 'tcp://127.0.0.1:7772'
        server = ServerManager(url, rpc_interface, name='Test Server')
        server.start()

        # 建立一个客户端连接
        with open_client(url) as client:
            client.ls_file()
            client.check_ip()

        # 停止服务器
        server.stop()


if __name__ == '__main__':
    unittest.main()