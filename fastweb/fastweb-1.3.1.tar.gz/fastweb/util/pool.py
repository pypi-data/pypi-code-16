# coding:utf8


import time
import json
import threading
from Queue import Queue, Empty

from fastweb.util.log import recorder
from fastweb import coroutine, ioloop, Return
from fastweb.pattern import SyncPattern, AsynPattern


DEFAULT_TIMEOUT = 80000


class ConnectionPool(object):
    """连接池"""

    def __init__(self, cls, setting, size, name, timeout=DEFAULT_TIMEOUT, maxconnections=None):
        """设置连接池

        连接池创建时尽量早的报错,运行过程中尽量去修复错误

        :parameter:
          - `cls`:连接池中实例化的类
          -`setting`:参数
          -`size`:连接池大小
          -`name`:连接池名字
          -`timeout`:连接最大超时时间,尝试重连时间
        """

        self._cls = cls
        self._pool = Queue()
        self._name = name
        self._size = size
        self._pattern = None
        self._timeout = timeout
        self._setting = setting
        self._used_pool = []
        self._unused_pool = []
        self._maxconnections = maxconnections
        self._lock = threading.Lock()

    def __str__(self):
        return '<{name}|ConnectionPool>'.format(name=self._name)

    def _create_connection_sync(self):
        """创建连接"""

        return self._cls(self._setting).set_name(self._name).connect()

    @coroutine
    def _create_connection_asyn(self):
        """创建连接"""

        connection = yield self._cls(self._setting).set_name(self._name).connect()
        raise Return(connection)

    def create_sync(self):
        """同步创建连接池"""

        self._pattern = SyncPattern
        recorder('DEBUG', 'synchronize connection pool create start <{name}>\n{setting}'.format(name=self._name, setting=json.dumps(self._setting,indent=4)))
        for _ in range(self._size):
            self.add_connection_sync()
        self.rescue(self._rescue_sync)
        recorder('DEBUG', 'synchronize connection pool create successful <{name}>'.format(name=self._name))

    @coroutine
    def create_asyn(self):
        """异步创建连接池"""

        self._pattern = AsynPattern
        recorder('DEBUG', 'asynchronous connection pool create start <{name}>\n{setting}'.format(name=self._name, setting=json.dumps(self._setting, indent=4)))
        for _ in range(self._size):
            yield self.add_connection_asyn()
        self.rescue(self._rescue_asyn)
        recorder('DEBUG', 'asynchronous connection pool create successful <{name}>'.format(name=self._name))

    def add_connection_sync(self):
        """同步增加连接"""

        connection = self._create_connection_sync()
        self._pool.put_nowait(connection)
        self._unused_pool.append(connection)

    @coroutine
    def add_connection_asyn(self):
        """同步增加连接"""

        connection = yield self._create_connection_asyn()
        self._pool.put_nowait(connection)
        self._unused_pool.append(connection)

    def remove_connection(self, connection):
        """移除连接"""

        pass

    def get_connection(self):
        """获取连接"""

        try:
            self._lock.acquire()
            connection = self._pool.get(block=True)
            self._unused_pool.remove(connection)
            self._lock.release()
            if self._pool.qsize() < 2:
                if self._pattern is AsynPattern:
                    self.scale_connections()
        except Empty:
            if self._pattern == SyncPattern:
                connection = self._create_connection_sync()
            elif self._pattern == AsynPattern:
                # connection = self._cls(self._setting).set_name(self._name)
                # yield connection.connect()
                # ioloop.IOLoop.current().add_future(future, lambda x: self._condition.notify())
                # coroutine(connection.connect)
                # ioloop.IOLoop.current().add_callback(connection.connect)
                # ioloop.IOLoop.current().add_future(future, lambda x: x)
                # ioloop.IOLoop.current().add_timeout()
                recorder('ERROR', '不能到这里')

            recorder('WARN', '<{name}> connection pool is empty,create a new connection {conn}'.format(name=self._name, conn=connection))

        self._used_pool.append(connection)
        recorder('DEBUG', '{obj} get connection {conn} {id}, left connections {count}'.format(obj=self, conn=connection, id=id(connection), count=self._pool.qsize()))
        return connection

    def lend_connection(self, timeout):
        """租用连接

        :parameter:
          `timeout`:租用时间,超过租用时间自动归还
        """
        pass

    def return_connection(self, connection):
        """归还连接

        :parameter:
          - `connection`:连接"""

        self._used_pool.remove(connection)
        self._unused_pool.append(connection)
        self._pool.put_nowait(connection)
        recorder('DEBUG', '<{name}> return connection {conn}, total connections {count}'.format(name=self._name, conn=connection, count=self._pool.qsize()))

    def _rescue_sync(self):
        """同步恢复连接
        目前先圈梁恢复
        """

        while True:
            time.sleep(self._timeout)
            recorder('INFO', '<{name}> rescue connection start'.format(name=self._name))
            for conn in self._unused_pool:
                conn.reconnect()
            recorder('INFO', '<{name}> rescue connection successful'.format(name=self._name))

    def _rescue_asyn(self):
        """同步恢复连接
        目前先圈梁恢复
        """

        while True:
            time.sleep(self._timeout)
            recorder('INFO', '<{name}> rescue connection start'.format(name=self._name))
            for conn in self._unused_pool:
                future = conn.reconnect()
                ioloop.IOLoop.instance().add_future(future, lambda x: x)
            recorder('INFO', '<{name}> rescue connection successful'.format(name=self._name))

    @staticmethod
    def rescue(target):
        """独立线程进行连接恢复"""

        threading.Thread(target=target).start()

    def _scale(self):
        recorder('WARN', '{obj} scale connection pool start'.format(obj=self))
        scale_loop = ioloop.IOLoop(make_current=True)
        scale_loop.run_sync(self.create_asyn)
        scale_loop.start()
        recorder('WARN', '{obj} scale connection pool successful'.format(obj=self))

    def scale_connections(self):
        threading.Thread(target=self._scale).start()


