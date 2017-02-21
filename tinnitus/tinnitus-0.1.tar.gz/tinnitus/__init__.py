from contextlib import contextmanager
from enum import Enum

import rpyc


_host = "localhost"
_port = 18861


class Status(Enum):

    PLAYING = 2
    PAUSED = 1
    STOPPED = 0


def configure(host=None, port=None):
    global _host
    global _port

    if host is not None:
        _host = host

    if port is not None:
        _port = host


@contextmanager
def remote():
    global _host
    global _port
    c = rpyc.connect(_host, _port)

    yield c.root

    c.close()