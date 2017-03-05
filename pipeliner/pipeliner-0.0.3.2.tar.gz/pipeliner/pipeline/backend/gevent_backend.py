import gevent

from .abstract import AbstractBackend
from pipeliner.exceptions import PipelineAlreadyRunning

from gevent import monkey
monkey.patch_all()


class GeventBackend(AbstractBackend):
    def __init__(self):
        self.is_running = False
        self._greenlet = None

    def run(self, target, *args, **kwargs):
        if self.is_running:
            raise PipelineAlreadyRunning()

        self.is_running = True
        self._greenlet = gevent.spawn(target, *args, **kwargs)

    def wait_until_complete(self):
        self._greenlet.join()
