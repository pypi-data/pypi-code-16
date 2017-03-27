# coding:utf8

"""服务层模块"""

from accesspoint import TServer, TSocket, TTransport, TBinaryProtocol

from fastweb.loader import app
from fastweb.util.log import recorder
from fastweb.util.process import FProcess
from fastweb.exception import ServiceError
from fastweb.web import SyncComponents, Components
from fastweb.util.python import load_module, to_iter
from fastweb.util.configuration import Configuration


DEFAULT_THREADPOOL_SIZE = 1000


class MicroService(object):
    """微服务类

    多个ABLogic组成一个微服务

    :parameter:
      - `name`:微服务名
      - `thrift_module`:thrift生成模块路径
      - `handlers`:处理句柄列表
    """

    def __init__(self, name, thrift_module, handlers):
        self.name = name
        self._module = thrift_module
        self._handler = to_iter(handlers)
        # TODO:handler合并应该遵守一些规则
        self._handler = type('Handler', self._handler, {})() if len(self._handler) > 1 else handlers

    def __str__(self):
        return '<MicroService|{name} {module}->{handler}>'.format(name=self.name,
                                                                  module=self._module,
                                                                  handler=self._handler)

    def start(self, port, size, daemon=True):
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
        recorder('INFO', '{svr} start at <{port}> threadpool size <{size}>'.format(svr=self, port=port, size=size))

        try:
            server.serve()
        except KeyboardInterrupt:
            recorder('INFO', '{svr} stop at <{port}>'.format(svr=self, port=port))


class ABLogic(SyncComponents):
    """基础逻辑类"""

    def __init__(self):
        super(ABLogic, self).__init__()


class Table(Components):
    """库表类"""

    def __init__(self):
        super(Table, self).__init__()


def start_server(config_path):
    """强制使用config的方式来配置微服务"""

    configuration = Configuration(config_path)
    microservices = configuration.get_components('microservice')

    for name, value in microservices.items():
        config = app.configs[name]
        name = value['object']

        port = config.get('port')
        if not port or not isinstance(port, int):
            recorder('CRITICAL', 'please specify port {conf}'.format(conf=config))
            raise ServiceError

        # 每个微服务只能在thrift中指定一个service,对应只有一个thrift模块
        thrift_module = config.get('thrift_module')
        if not thrift_module or not isinstance(thrift_module, str):
            recorder('CRITICAL', 'please specify thrift_module {conf}'.format(conf=config))
            raise ServiceError

        handlers = config.get('handlers')
        if not handlers or isinstance(handlers, (str, list)):
            recorder('CRITICAL', 'please specify handlers {conf}'.format(conf=config))
            raise ServiceError

        daemon = config.get('daemon', True)
        # 默认微服务不活跃
        active = config.get('active', False)
        size = config.get('size', DEFAULT_THREADPOOL_SIZE)

        if active:
            microservice = MicroService(name, thrift_module=thrift_module, handler=handlers)
            process = FProcess(name='microservice', task=microservice.start, port=port, size=size, daemon=daemon)
            process.start()
