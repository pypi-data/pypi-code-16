#!/usr/bin/env python
# -*-coding:utf-8-*-
# 测验rpc服务器执行Linux系统命令

import unittest
from xnrpc.server import RpcInterface, ServerManager
from xnrpc.client import open_client
from xnrpc.subproc import proc_cmd
from xnrpc.common.log import get_log
_log = get_log(__name__)


class OperationRpcInterface(RpcInterface):

    def ls_file(self):
        """两种调用方法"""
        _log.info('Operation ls file, now is true')
        args = ['ls', '-l']
        retcode1, stdout1, stderr1 = proc_cmd(args, sudo=True, timeout=10)
        _log.info('Operation ls file, stdout1={}'.format(stdout1))
        args = 'ls -l'
        retcode2, stdout2, stderr2 = proc_cmd(args, sudo=True, timeout=10)
        _log.info('Operation ls file, stdout2={}'.format(stdout2))
        return None

    def check_ip(self):
        """管道命令"""
        _log.info('Operation check ip, now is true')
        args = "hostname -I | awk '{print $1}'"
        retcode2, stdout3, stderr2 = proc_cmd(args, sudo=True, timeout=10)
        _log.info('Operation check ip, stdout3={}'.format(stdout3))
        return None


class RpcTest(unittest.TestCase):
    def test_server_manager(self):
        # 启动RPC服务器
        rpc_interface = OperationRpcInterface
        url = 'tcp://127.0.0.1:7773'
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