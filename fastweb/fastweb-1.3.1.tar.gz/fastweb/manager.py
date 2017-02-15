# coding:utf8

"""组件管理模块"""

import json

import fastweb.loader
from fastweb import coroutine
from fastweb.util.log import recorder
from fastweb.util.pool import ConnectionPool
from fastweb.setting.default_connection_component import SYNC_CONN_COMPONENTS, ASYN_CONN_COMPONENTS
from fastweb.exception import ConfigurationError, ComponentError, ManagerError, ConnectionPoolError


class Manager(object):
    """管理器

    fastweb.setting.default_connection_component.SYNC_CONN_COMPONENTS
    fastweb.setting.default_connection_component.ASYN_CONN_COMPONENTS
    存储组件名称及相应的组件类
    """

    def __init__(self):
        """
        _pool:{component_name: component_pool}
        """

        self._pools = {}

    def setup_sync(self):
        """同步安装组件

        初始化组件时,尽快的抛出准确的错误信息
        """

        recorder('DEBUG', 'synchronize manager setup start')

        if fastweb.loader.app.configer:
            # 连接池组件创建
            for (cpre, cls, default_size) in SYNC_CONN_COMPONENTS:
                components = fastweb.loader.app.configer.get_components(cpre)

                for name, value in components.items():
                    config = fastweb.loader.app.configs[name]
                    size = int(config.get('size', default_size))
                    pool = ConnectionPool(cls, config, size, name)
                    pool.create_sync()
                    self._pools[value['object']] = pool
        
        recorder('DEBUG', 'synchronize manager setup successful')

    @coroutine
    def setup_asyn(self):
        """异步安装组件

        初始化组件时,尽快的抛出准确的错误信息
        """

        recorder('DEBUG', 'asynchronous manager setup start')

        if fastweb.loader.app.configer:
            # 连接池组件创建
            for (cpre, cls, default_size) in ASYN_CONN_COMPONENTS:
                components = fastweb.loader.app.configer.get_components(cpre)

                for name, value in components.items():
                    config = fastweb.loader.app.configs[name]
                    size = int(config.get('size', default_size))
                    pool = ConnectionPool(cls, config, size, name)
                    yield pool.create_asyn()
                    self._pools[value['object']] = pool

        recorder('DEBUG', 'asynchronous manager setup successful')

    def get_component(self, name, obj):
        """通过manager获取组件

        ManagerError:可能是配置文件错误或者程序错误,应该尽快进行处理,不应该再向下继续运行

        :parameter:
          - `name`:组件名称"""

        pool = self._pools.get(name)

        if pool:
            component = pool.get_connection()
            component.set_used(obj.recorder)
            return component
        else:
            recorder('CRITICAL', 'please check configuration\n{conf}\n{name}'.format(conf=json.dumps(fastweb.loader.app.configs), name=name))
            raise ManagerError

    def return_component(self, name, component):
        """归还组件

        :parameter:
          - `name`:组件名称
          - `component`:组件
        """

        pool = self._pools.get(name)

        if pool:
            pool.return_connection(component)
            component.set_idle()
        else:
            recorder('CRITICAL',
                     'please check configuration\n{conf}\n{name}'.format(conf=json.dumps(fastweb.loader.app.configs),
                                                                         name=name))
            raise ManagerError

