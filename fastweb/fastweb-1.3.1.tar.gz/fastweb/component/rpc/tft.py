# coding:utf8

import six
import sys
from thrift import TTornado
from importlib import import_module
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from fastweb import coroutine
from fastweb.exception import RpcError, ConfigurationError
from fastweb.util.log import recorder
from fastweb.component import Component
from fastweb.util.python import AsynProxyCall, ExceptionProcessor


class SyncRpc(Component):
    """Thrift Rpc同步组件"""

    eattr = {'host': str, 'port': int, 'servise_name': str, 'module': str}

    def __init__(self, **kwargs):
        super(SyncRpc, self).__init__(**kwargs)

        self.isConnect = False

    def __str__(self):
        return '<SyncThriftRpc {name} {host} {port} {module_path} {module}>'.format(
            host=self.host,
            port=self.port,
            module_path=self.thrift_module_path,
            module=self.thrift_module,
            name=self.name)

    def connect(self):
        if isinstance(self.module, six.string_types):
            module = import_module(self.module)
        else:
            self.recorder('ERROR', '{obj} module [{module}] error'.format(obj=self, module=self.module))
            raise ConfigurationError

        try:
            transport = TSocket.TSocket(host, port)
            self._transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            pfactory = TMultiplexedProtocol.TMultiplexedProtocol(protocol, service_name)
            self._transport.open()
            self.client = getattr(module, 'Client')(pfactory)
        except:
            raise RpcError

    def __getattr__(self, name):
        if hasattr(self.client, name):
            return getattr(self.client, name)

    def close(self):
        self.transport.close()


class AsynRpc(Component):
    """Thrift Rpc异步组件"""

    eattr = {'host':str, 'port':int, 'thrift_module_path':str, 'thrift_module':str}

    def __init__(self, **kwargs):
        super(AsynRpc, self).__init__(**kwargs)

    def __str__(self):
        return '<AsynThriftRpc {host} {port} {module_path} {module} {name}>'.format(
            host=self.host,
            port=self.port,
            module_path=self.thrift_module_path,
            module=self.thrift_module,
            name=self.name)

    @coroutine
    def connect(self):
        """建立连接"""

        self.client = None
        self.host = self.kwargs['host']
        self.port = self.kwargs['port']
        self.thrift_module_path = self.kwargs['thrift_module_path']
        self.thrift_module = self.kwargs['thrift_module']
        sys.path.append(self.thrift_module_path)

        if isinstance(self.thrift_module, six.string_types):
            self.module = import_module(self.thrift_module)

        self.transport = TTornado.TTornadoStreamTransport(self.host, self.port)
        yield self._connect()
        self.set_idle()
        protocol = TBinaryProtocol.TBinaryProtocolFactory()
        self.client = getattr(self.module, 'Client')(self.transport, protocol)
        self._other = self.client

    @coroutine
    def _connect(self):
        try:
            yield self.transport.open()
        except TTransport.TTransportException as ex:
            self.recorder('ERROR', '{obj} connect error ({e})'.format(obj=self, e=ex) ) if self.recorder else recorder('ERROR', '{obj} connect error ({e})'.format(obj=self, e=ex) )
            raise RpcError

    def __getattr__(self, name):
        """获取远程调用方法"""

        exception_processor = ExceptionProcessor(AttributeError, self._connect)

        if hasattr(self.client, name):
            return AsynProxyCall(self, name, throw_exception=RpcError, exception_processor=exception_processor)
        else:
            raise AttributeError
        
    def close(self):
        """关闭连接"""

        if self.transport:
            self.transport.close()

    def __del__(self):
        self.close()

