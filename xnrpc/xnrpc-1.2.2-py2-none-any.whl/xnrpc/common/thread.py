#!/usr/bin/env python
# -*-coding:utf-8-*-

import gevent.event
import gevent.greenlet
from xnrpc.common.log import get_log
_log = get_log(__name__)

WAIT_INTERVAL = 5


class ServerThread(gevent.greenlet.Greenlet):
    """gevent服务器协程"""
    def __init__(self):
        super(ServerThread, self).__init__()
        self._complete = gevent.event.Event()

    def _run(self):
        _log.info("Start %s" % self.__class__.__name__)
        while not self._complete.is_set():
            try:
                _log.debug("Enter...")
                self.work()
            except:
                _log.error("Work exception...", exc_info=1)
            finally:
                self._complete.wait(WAIT_INTERVAL)
        _log.info("Completed %s" % self.__class__.__name__)

    def work(self):
        """覆盖这个方法"""
        pass

    def stop(self):
        _log.info("%s stopping", self.__class__.__name__)
        self._complete.set()
