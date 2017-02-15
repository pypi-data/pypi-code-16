#!/usr/bin/env python
# -*-coding:utf-8-*-

import time
import gevent
import zerorpc
from xnrpc.common.log import get_log
_log = get_log(__name__)


class ServerManager(object):
    def __init__(self, url, rpc_interface, heartbeat=None, name=None):
        self.rpc_server_last_service_time = None
        self.rpc_server = zerorpc.Server(rpc_interface(self), heartbeat=heartbeat)
        self.rpc_server.bind(url)
        self.rpc_gthread = None
        self.name = name

    def start(self):
        _log.info("{} starting".format(self.name))
        self.rpc_gthread = gevent.spawn(self.rpc_server.run)
        _log.info("{} rpc server started".format(self.name))

    def stop(self):
        _log.info("{} stopping".format(self.name))
        self.rpc_server.stop()
        _log.info("{} rpc server stopped".format(self.name))

    def join(self):
        self.rpc_gthread.join()


class RpcInterface(object):
    def __init__(self, manager=None):
        self._manager = manager
        if self._manager and not self._manager.rpc_server_last_service_time:
            self._manager.rpc_server_last_service_time = time.time()
        # 100 ms is too slow
        self.SLOW_THRESHOLD = 0.1

    def __getattribute__(self, item):
        """
        Wrap functions with logging
        """
        if item.startswith('_'):
            return object.__getattribute__(self, item)
        else:
            attr = object.__getattribute__(self, item)
            if callable(attr):
                def wrap(*args, **kwargs):
                    _log.debug("RpcInterface >> %s", item)
                    try:
                        begin_time = time.time()
                        if self._manager:
                            self._manager.rpc_server_last_service_time = begin_time
                        rc = attr(*args, **kwargs)
                        end_time = time.time()
                        elapse_time = end_time - begin_time
                        if elapse_time > self.SLOW_THRESHOLD:
                            _log.warn("Slow proccess '%s', %sms", item, elapse_time * 1000)
                        else:
                            _log.debug("RpcInterface << %s %sms", item, elapse_time * 1000.0)
                    except:
                        _log.exception("RpcInterface exception, %s" % item)
                        raise
                    return rc

                return wrap
            else:
                return attr

