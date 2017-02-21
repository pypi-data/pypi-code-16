import threading

import rpyc
import sys

from tinnitus import Status
from tinnitus.pluggable import Pluggable
from tinnitus.queue import Queue


_status = Status.STOPPED  # type: Status
_queue = Queue()  # type: Queue
_pluggable = Pluggable()  # type: Pluggable
_lock = threading.Lock()  # type: threading.Lock


def _play_next(*args, **kwargs):
    global _queue
    global _status

    _queue.next()
    resource_id, mrl, backend = _queue.current

    if resource_id is None:
        _pluggable.backend.stop()

    _pluggable.use_backend(backend)
    _pluggable.backend.set_mrl(mrl)
    _pluggable.backend.play()

    with _lock:
        _status = Status.PLAYING


_pluggable.set_callback(_play_next)


class PlayerService(rpyc.Service):

    def on_connect(self): pass

    def on_disconnect(self): pass

    def exposed_add(self, resource_id: int, mrl: str, backend: str) -> None:
        global _queue
        _queue.add(resource_id, mrl, backend)

    def exposed_remove(self, resource_id: int) -> None:
        global _queue
        _queue.remove(resource_id)

    def exposed_clear(self) -> None:
        global _queue
        _queue.clear()

    def exposed_current(self) -> None:
        global _queue
        resource_id, mrl, backend = _queue.current
        return resource_id

    def exposed_queue(self) -> None:
        global _queue
        return _queue.queue

    def exposed_play(self) -> None:
        global _status
        global _lock

        if _status == Status.PLAYING:
            return

        if _status == Status.STOPPED:
            _play_next()

        elif _status == Status.PAUSED:
            _pluggable.backend.play()

        with _lock:
            _status = Status.PLAYING

    def exposed_pause(self) -> None:
        global _pluggable
        global _status
        global _lock

        if _status != Status.PAUSED:
            _pluggable.backend.pause()

            with _lock:
                _status = Status.PAUSED

    def exposed_stop(self) -> None:
        global _queue
        global _pluggable
        global _status
        global _lock

        if _status != Status.STOPPED:
            _pluggable.backend.stop()
            _queue.put_back()

            with _lock:
                _status = Status.STOPPED

    def exposed_play_next(self) -> None:
        global _status
        global _lock

        if _status != Status.STOPPED:
            _play_next()

            with _lock:
                _status = Status.PLAYING

    def exposed_status(self) -> Status:
        global _status
        global _lock

        with _lock:
            status = _status

        return status


def run_command():

    argc = len(sys.argv)
    port = 18861

    if argc > 2:
        print("Usage...")
        sys.exit(1)

    if argc > 1:
        port = int(sys.argv[1])

    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(PlayerService, port=port)
    t.start()
