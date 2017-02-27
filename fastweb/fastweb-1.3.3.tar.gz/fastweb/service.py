# coding:utf8

from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from fastweb.util.log import recorder
from fastweb.web import SyncComponents, Components
from fastweb.util.python import load_module, to_iter


class MicroServices(object):
    """通过配置文件来启动服务
    或者通过command启动服务
    """
    pass


class MicroService(object):
    """微服务
    多个AbLogic组成一个微服务
    """

    def __init__(self, name, thrift_module, handler):
        self.name = name
        self._module = thrift_module
        self._handler = to_iter(handler)
        # TODO:handler合并应该遵守一些规则
        self._handler = type('Handler', self._handler, {})() if len(self._handler) > 1 else handler

    def start(self, port, size=1000, daemon=True):
        """微服务开始

        生成一个微服务

        :parameter:
         - `handler`:AbLogic列表
        """

        # 将所有的handlers合并成一个handler
        module = load_module(self._module)
        processor = getattr(module, 'Processor')(self._handler())
        transport = TSocket.TServerSocket(port=port)
        tfactory = TTransport.TFramedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory, daemon=daemon)
        server.setNumThreads(size)
        recorder('INFO', 'thrift server start at <{port}> threadpool size <{size}>'.format(port=port, size=size))
        server.serve()


class AbLogic(SyncComponents):
    """基础逻辑"""
    pass


class Table(Components):
    """数据库表"""
    pass



