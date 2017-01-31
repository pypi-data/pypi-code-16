#!/usr/bin/python

from __future__ import unicode_literals

import os

from . import core
try:
    import resource
    _PAGESIZE = resource.getpagesize()
except ImportError:
    # Not Unix
    _PAGESIZE = 4096


class ProcessCollector(object):
    """Collector for Standard Exports such as cpu and memory."""
    def __init__(self, namespace='', pid=lambda: 'self', proc='/proc', registry=core.REGISTRY):
        self._namespace = namespace
        self._pid = pid
        self._proc = proc
        if namespace:
            self._prefix = namespace + '_process_'
        else:
            self._prefix = 'process_'
        self._ticks = 100.0
        try:
            self._ticks = os.sysconf('SC_CLK_TCK')
        except (ValueError, TypeError, AttributeError):
            pass

        # This is used to test if we can access /proc.
        self._btime = 0
        try:
            self._btime = self._boot_time()
        except IOError:
            pass
        if registry:
            registry.register(self)

    def _boot_time(self):
        with open(os.path.join(self._proc, 'stat')) as stat:
            for line in stat:
                if line.startswith('btime '):
                    return float(line.split()[1])

    def collect(self):
        if not self._btime:
            return []

        pid = os.path.join(self._proc, str(self._pid()).strip())

        result = []
        try:
            with open(os.path.join(pid, 'stat')) as stat:
                parts = (stat.read().split(')')[-1].split())
            vmem = core.GaugeMetricFamily(self._prefix + 'virtual_memory_bytes',
                                          'Virtual memory size in bytes.', value=float(parts[20]))
            rss = core.GaugeMetricFamily(self._prefix + 'resident_memory_bytes', 'Resident memory size in bytes.',
                                         value=float(parts[21]) * _PAGESIZE)
            start_time_secs = float(parts[19]) / self._ticks
            start_time = core.GaugeMetricFamily(self._prefix + 'start_time_seconds',
                                                'Start time of the process since unix epoch in seconds.',
                                                value=start_time_secs + self._btime)
            utime = float(parts[11]) / self._ticks
            stime = float(parts[12]) / self._ticks
            cpu = core.CounterMetricFamily(self._prefix + 'cpu_seconds_total',
                                           'Total user and system CPU time spent in seconds.',
                                           value=utime + stime)
            result.extend([vmem, rss, start_time, cpu])
        except IOError:
            pass

        try:
            with open(os.path.join(pid, 'limits')) as limits:
                for line in limits:
                    if line.startswith('Max open file'):
                        max_fds = core.GaugeMetricFamily(self._prefix + 'max_fds',
                                                         'Maximum number of open file descriptors.',
                                                         value=float(line.split()[3]))
                        break
            open_fds = core.GaugeMetricFamily(self._prefix + 'open_fds',
                                              'Number of open file descriptors.',
                                              len(os.listdir(os.path.join(pid, 'fd'))))
            result.extend([open_fds, max_fds])
        except IOError:
            pass

        return result


PROCESS_COLLECTOR = ProcessCollector()
"""Default ProcessCollector in default Registry REGISTRY."""
