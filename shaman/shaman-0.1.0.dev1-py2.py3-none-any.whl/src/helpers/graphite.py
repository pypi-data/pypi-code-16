from pyformance import MetricsRegistry
from pyformance.reporters import CarbonReporter
import socket
import traceback


class GraphiteSender(object):
    def __init__(self, host, port, global_key, worker_name, metrics_name, logger, enabled=True):
        self._logger = logger
        try:
            self.enabled = enabled
            if self.enabled:
                self.hostname = socket.gethostname().split('.')[0]

                self.registry = MetricsRegistry()
                self.global_key = global_key + '.' + self.hostname + '.' + worker_name + '.'

                self.reporter = CarbonReporter(registry=self.registry, reporting_interval=1, prefix=self.global_key,
                                               server=host, port=port)
                self.reporter.start()

            self.after_init(host, port, global_key, worker_name, metrics_name, enabled)
        except Exception as e:
            self._logger.error('GraphiteSender exception: {}'.format(e))
            self._logger.error('GraphiteSender traceback: {}'.format(traceback.format_exc()))


class GraphiteSenderTimer(GraphiteSender):
    def after_init(self,host, port, global_key, worker_name, metrics_name, enabled=True):
        self._timer = self.registry.timer(metrics_name)

    def start_timer(self):
        if self.enabled:
            self.ts = self._timer.time()

    def stop_timer(self):
        if self.enabled:
            self.ts.stop()

    def timeit_graphite(self, method):
        def returned_method(*args,**kwargs):
            self.start_timer()
            result = method(*args,**kwargs)
            self.stop_timer()
            return result
        return returned_method


class GraphiteSenderCounter(GraphiteSender):
    def after_init(self, host, port, global_key, worker_name, metrics_name, enabled=True):
        self._counter = self.registry.meter(metrics_name)

    def increase_counter(self):
        if self.enabled:
            self._counter.mark()

