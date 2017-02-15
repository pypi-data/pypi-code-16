#!/usr/bin/env python
#-*-coding:utf-8-*-
"""
The Resource class is a base class for all resource type.
"""
import time
import gevent
import zerorpc
from collections import defaultdict
from contextlib import contextmanager
from xnrpc.common.log import get_log

_log = get_log(__name__)


@contextmanager
def open_client(url, timeout=10, heartbeat=None):
    client = RpcClient(url, timeout=timeout, heartbeat=heartbeat)
    try:
        yield client
    except:
        _log.error('rpc client error.', exc_info=1)
    finally:
        client.close()


class RpcClient(zerorpc.Client):

    def __init__(self, url, slow_threshold=0.2,
                 max_perf_count=10, profile=False, timeout=10, heartbeat=None):
        super(RpcClient, self).__init__(timeout=timeout, heartbeat=heartbeat)
        self.URL = url
        self.slow_threshold = slow_threshold
        self.max_perf_count = max_perf_count
        self.profile = profile
        self.method_times = defaultdict(list)
        _log.debug("Conneting %s", self.URL)
        self.connect(self.URL)

    def _process_response(self, request_event, bufchan, timeout):
        begin_time = time.time()
        result = super(RpcClient, self)._process_response(request_event, bufchan, timeout)
        end_time = time.time()
        elapse_time = end_time - begin_time
        _log.debug("RPC elapse time '%s' %sms", request_event.name, elapse_time * 1000)
        if elapse_time > self.slow_threshold:
            _log.warn("Slow RPC '%s' %sms", request_event.name, elapse_time * 1000)

        if self.profile:
            self.method_times[request_event.name].append(elapse_time)
            self._report()
        return result

    def _report(self):
        for method_name, times in self.method_times.items():
            if len(times) < self.max_perf_count:
                continue
            _log.debug("RPC timing for '%s': %s/%s/%s avg/max/min(ms) times: %s",
                      method_name,
                      sum(times) * 1000.0 / len(times),
                      max(times) * 1000.0,
                      min(times) * 1000.0,
                      len(times))
            if len(times) >= self.max_perf_count:
                self.method_times[method_name] = []


class TimeoutRpcClient(object):
    def __init__(self, name, rpc_new_fn, default_time_out=10, elaspe_time_step=5):
        self._name = name
        self._new_instance_fn = rpc_new_fn
        self._event_wait = gevent.event.Event()
        self._default_time_out = default_time_out
        if self._default_time_out <= 0:
            self._default_time_out = 60
        self._elaspe_time_step = elaspe_time_step
        if self._elaspe_time_step < 0:
            self._elaspe_time_step = 5
        self._instance = None
        self._timeout = 0

    def get_instance(self):
        if not self._instance:
            _log.info("New rpc %s", self._name)
            self._instance = self._new_instance_fn()
            gevent.spawn(self._close_instance)
        self._timeout = self._default_time_out
        return self._instance

    def _close_instance(self):
        while True:
            self._event_wait.wait(self._elaspe_time_step)
            self._timeout -= self._elaspe_time_step
            if self._timeout <= 0:
                break
        _log.info("Close rpc %s", self._name)
        if self._instance:
            self._instance.close()
        self._instance = None
        self._timeout = 0