# coding:utf8


import pymysql 
import tornado_mysql
from tornado import iostream
from tornado.locks import Condition

from fastweb import ioloop
import fastweb.util.tool as tool
from fastweb import coroutine, Return
from fastweb.component import Component
from fastweb.exception import MysqlError
from fastweb.util.tool import Retry, RetryPolicy


DEFAULT_PORT = 3306
DEFAULT_TIMEOUT = 5
DEFAULT_CHARSET = 'utf8'
DEFAULT_AUTOCOMMIT = True


def str_sql(v):
    """特殊类型转换成sql字符串"""

    if v is None:
        return 'NULL'
    return v


class Mysql(Component):
    """Mysql基类"""

    eattr = {'host': str}
    oattr = {'port': int, 'user': str, 'password': str, 'db': str, 'timeout': int, 'charset': str, 'autocommit': bool}

    def __init__(self, setting):
        self.port = DEFAULT_PORT
        self.charset = DEFAULT_CHARSET
        self.timeout = DEFAULT_TIMEOUT
        self.autocommit = DEFAULT_AUTOCOMMIT

        super(Mysql, self).__init__(setting)

        self.isConnect = False
        self._conn = None
        self._cur = None
        self._event = False

        self._sql = None
        self._kwargs = None

        self._prepare()

    def _prepare(self):
        self.setting['passwd'] = self.setting.pop('password', None)
        self.setting['connect_timeout'] = self.setting.pop('timeout', None)

    def connect(self):
        raise NotImplementedError

    def reconnect(self):
        raise NotImplementedError

    def start_event(self):
        raise NotImplementedError

    def exec_event(self, sql, **kwargs):
        raise NotImplementedError

    def end_event(self):
        """结束事务
        如果不结束,则事务无效果,事务虽然无效但是会占用id
        """

        raise NotImplementedError

    def query(self, sql, **kwargs):
        raise NotImplementedError

    def fetch(self):
        """获取一条结果"""

        return self._cur.fetchone()

    def fetchall(self):
        """获取全部结果"""

        return self._cur.fetchall()

    def error(self):
        """错误状态"""

        self._event = False
        self.isConnect = False

    def close(self):
        """关闭连接"""

        raise NotImplementedError

    def rollback(self):
        """事务回滚"""

        raise NotImplementedError

    def commit(self):
        """事务提交"""
        raise NotImplementedError

    @property
    def efficetid(self):
        """返回effectid"""

        return int(self._conn.insert_id())


class SyncMysql(Mysql):
    """同步mysql
       线程不安全"""

    def __str__(self):
        return '<SyncMysql {name} {host} {port} {user} {db} {charset}>'.format(
            host=self.host,
            port=self.port,
            user=self.user,
            db=self.db,
            name=self.name,
            charset=self.charset)

    def connect(self):
        """建立连接"""

        # 判断在二次连接时关闭之前的连接
        if self.isConnect:
            self.close()

        try:
            self.recorder('INFO', '{obj} connect start'.format(obj=self))
            self._conn = pymysql.connect(**self.setting)
            self._cur = self._conn.cursor(pymysql.cursors.DictCursor)
            self.isConnect = True
            self.recorder('INFO', '{obj} connect successful'.format(obj=self))
        except pymysql.Error as e:
            self.recorder('ERROR', '{obj} connect failed [{msg}]'.format(obj=self, msg=e))
            self.error()
            raise MysqlError

        return self

    def reconnect(self):
        """重新连接"""

        self.recorder('WARN', '{obj} reconnect start'.format(obj=self))

        try:
            self._conn.ping()
            self.isConnect = True
        except pymysql.Error as e:
            self.recorder('ERROR', '{obj} reconnect error [{msg}]'.format(msg=e))
            self.error()
            raise MysqlError

        self.recorder('WARN', '{obj} reconnect successful'.format(obj=self))

    def start_event(self):
        """事务开始"""

        try:
            self._event = True
            self.recorder('INFO', '{obj} start event'.format(obj=self))
            self._conn.begin()
        except pymysql.OperationalError as e:
            self.recorder('WARN', '{obj} event start error [{msg}]'.format(msg=e))
            self.reconnect()
            self.start_event()

    def exec_event(self, sql, **kwargs):
        """事务执行"""

        if self._event:
            self.recorder('INFO', '{obj} execute event'.format(obj=self))
            return self.query(sql, **kwargs)
        else:
            self.recorder('CRITICAL', 'please start event first!')
            raise MysqlError

    def end_event(self):
        """事务结束"""

        if self._event:
            self._event = False
            self.recorder('INFO', '{obj} end event'.format(obj=self))
            self.commit()
        else:
            self.recorder('CRITICAL', 'please start event first! ')
            raise MysqlError

    def query(self, sql, **kwargs):
        """查询sql"""

        Retry('{obj}'.format(obj=self), self._query, sql, obj=self, **kwargs).run_sync()

    def _query(self, sql, **kwargs):
        mysql_retry_policy = RetryPolicy(times=1, error=MysqlError)

        try:
            self._kwargs = kwargs = {k:str_sql(v) for k,v in kwargs.iteritems()}
            self._sql = sql = sql.format(**kwargs)

            self.recorder('INFO', '{obj} query start\n{sql}'.format(obj=self, sql=sql))
            with tool.timing('s', 10) as t:
                self._cur.execute(sql)
            self.recorder('INFO', '{obj} query successful\n{sql}\t[{time}]\t[{effect}]'.format(obj=self, sql=sql, time=t, effect=self._cur.rowcount))
        except pymysql.OperationalError as e:
            self.recorder('ERROR', '{obj} mysql has gone away [{msg}]'.format(obj=self, msg=e))
            self.isConnect = False
            self.reconnect()
            # 执行过程中的重试,只重试一次
            raise mysql_retry_policy
        except (pymysql.IntegrityError, pymysql.ProgrammingError) as e:
            self.recorder('ERROR', '{obj} query error\n{sql}\n[{msg}]'.format(obj=self, sql=sql, msg=e))
            raise MysqlError
        except (KeyError, TypeError) as e:
            self.recorder('ERROR', '{obj} sql format error\n{sql}\n{kwargs}\n[{msg}]'.format(obj=self, sql=sql, kwargs=kwargs, msg=e))
            raise MysqlError

        # 非事务状态下立刻提交
        if not self._event:
            self.commit()

        return self._cur.rowcount

    def error(self):
        """错误状态"""

        self._event = False
        self.isConnect = False

    def close(self):
        """关闭连接"""

        self.recorder('INFO', '{obj} connection close start'.format(obj=self))
        self._cur.close()
        self._conn.close()
        self.recorder('INFO', '{obj} connection close successful'.format(obj=self))

    def rollback(self):
        """事务回滚
        # TODO:记录本次事务语句
        """

        self._conn.rollback()
        self.recorder('INFO', '{obj} query rollback'.format(obj=self))

    def commit(self):
        """事务提交"""

        self._conn.commit()
        self.recorder('INFO', '{obj} query commit'.format(obj=self))


class AsynMysql(Mysql):
    """异步mysql组件"""

    def __str__(self):
        return '<AsynMysql {host} {port} {user} {db} {name} {charset}>'.format(
            host=self.host,
            port=self.port,
            user=self.user,
            db=self.db,
            name=self.name,
            charset=self.charset)

    @coroutine
    def connect(self):
        """建立连接"""

        try:
            self.recorder('INFO', '{obj} connect start'.format(obj=self))
            self._conn = yield tornado_mysql.connect(**self.setting)
            self.isConnect = True
            self.recorder('INFO', '{obj} connect successful'.format(obj=self))
        except tornado_mysql.Error as e:
            self.recorder('ERROR', '{obj} connect failed [{msg}]'.format(obj=self, msg=e))
            self.error()
            raise MysqlError

        raise Return(self)

    @coroutine
    def reconnect(self):
        """重新连接"""

        self.recorder('WARN', '{obj} reconnect start'.format(obj=self))

        try:
            yield self._conn.ping()
            self.isConnect = True
        except tornado_mysql.Error as e:
            self.recorder('ERROR', '{obj} reconnect error [{msg}]'.format(obj=self, msg=e))
            self.error()
            raise MysqlError

        self.recorder('WARN', '{obj} reconnect successful'.format(obj=self))

    @coroutine
    def start_event(self):
        """事务开始"""

        try:
            self._event = True
            self.recorder('INFO', '{obj} start event'.format(obj=self))
            yield self._conn.begin()
        except tornado_mysql.OperationalError as e:
            self.recorder('WARN', '{obj} event start error [{msg}]'.format(msg=e))
            yield self.reconnect()
            yield self.start_event()

    @coroutine
    def exec_event(self, sql, **kwargs):
        """事务执行"""

        if self._event:
            self.recorder('INFO', '{obj} execute event'.format(obj=self))
            rows = yield self.query(sql, **kwargs)
            raise Return(rows)
        else:
            self.recorder('CRITICAL', 'please start event first!')
            raise MysqlError

    @coroutine
    def end_event(self):
        """事务结束"""

        if self._event:
            self._event = False
            self.recorder('INFO', '{obj} end event'.format(obj=self))
            yield self.commit()
        else:
            self.recorder('CRITICAL', 'please start event first! ')
            raise MysqlError

    @coroutine
    def query(self, sql, **kwargs):
        """查询sql"""
        if not self._event:
            self._cur = self._conn.cursor(tornado_mysql.cursors.DictCursor)
        #yield self._query(sql, **kwargs)
        yield Retry('{obj}'.format(obj=self), self._query, self, sql, **kwargs).run_asyn()

    @coroutine
    def _query(self, sql, **kwargs):
        mysql_retry_policy = RetryPolicy(times=1, error=MysqlError)

        try:
            self._kwargs = kwargs = {k: str_sql(v) for k, v in kwargs.iteritems()}
            self._sql = sql = sql.format(**kwargs)

            self.recorder('INFO', '{obj} query start\n{sql}'.format(obj=self, sql=sql))
            with tool.timing('ms', 10) as t:
                import pdb
                # pdb.set_trace()
                self.recorder('DEBUG', 'timing...')
                yield self._cur.execute(sql)
            self.recorder('INFO',
                          '{obj} query successful\n{sql}\t[{time}]\t[{effect}]'.format(obj=self, sql=sql, time=t,                                                                 effect=self._cur.rowcount))
        except (tornado_mysql.OperationalError, tornado_mysql.InterfaceError, iostream.StreamClosedError) as e:
            self.recorder('ERROR', '{obj} mysql has gone away [{msg}]'.format(obj=self, msg=e))
            self.isConnect = False
            yield self.reconnect()
            # 执行过程中的重试,只重试一次
            raise mysql_retry_policy
        except (tornado_mysql.IntegrityError, tornado_mysql.ProgrammingError) as e:
            self.recorder('ERROR', '{obj} query error\n{sql}\n[{msg}]'.format(obj=self, sql=sql, msg=e))
            raise MysqlError
        except (KeyError, TypeError) as e:
            self.recorder('ERROR',
                          '{obj} sql format error\n{sql}\n{kwargs}\n[{msg}]'.format(obj=self, sql=sql, kwargs=kwargs,
                                                                                    msg=e))
            raise MysqlError

        # 非事务状态下立刻提交
        if not self._event:
            yield self.commit()
            yield self._cur.close()

        raise Return(self._cur.rowcount)

    @coroutine
    def rollback(self):
        """回滚"""

        yield self._conn.rollback()

    @coroutine
    def commit(self):
        """提交操作"""

        yield self._conn.commit()
    
    @coroutine
    def close(self):
        """关闭连接"""

        yield self._cur.close()
        yield self._conn.close()

