# coding=UTF-8
from __future__ import absolute_import, division, print_function
import six
import logging
import select
import monotonic
import socket
import collections
import heapq

from coolamqp.uplink.listener.socket import SocketFailed, BaseSocket


logger = logging.getLogger(__name__)


RO = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
RW = RO | select.EPOLLOUT


class EpollSocket(BaseSocket):
    """
    EpollListener substitutes your BaseSockets with this
    """
    def __init__(self, sock, on_read, on_fail, listener):
        BaseSocket.__init__(self, sock, on_read=on_read, on_fail=on_fail)
        self.listener = listener
        self.priority_queue = collections.deque()

    def send(self, data, priority=False):
        """
        This can actually get called not by ListenerThread.
        """
        BaseSocket.send(self, data, priority=priority)
        try:
            self.listener.epoll.modify(self, RW)
        except socket.error:
            # silence. If there are errors, it's gonna get nuked soon.
            pass

    def oneshot(self, seconds_after, callable):
        """
        Set to fire a callable N seconds after
        :param seconds_after: seconds after this
        :param callable: callable/0
        """
        self.listener.oneshot(self, seconds_after, callable)

    def noshot(self):
        """
        Clear all time-delayed callables.

        This will make no time-delayed callables delivered if ran in listener thread
        """
        self.listener.noshot(self)


class EpollListener(object):
    """
    A listener using epoll.
    """

    def __init__(self):
        self.epoll = select.epoll()
        self.fd_to_sock = {}
        self.time_events = []

    def wait(self, timeout=1):
        events = self.epoll.poll(timeout=timeout)

        # Timer events
        mono = monotonic.monotonic()
        while len(self.time_events) > 0 and (self.time_events[0][0] < mono):
            ts, fd, callback = heapq.heappop(self.time_events)
            callback()

        for fd, event in events:
            sock = self.fd_to_sock[fd]

            # Errors
            try:
                if event & (select.EPOLLERR | select.EPOLLHUP):
                    raise SocketFailed()

                if event & select.EPOLLIN:
                    sock.on_read()

                if event & select.EPOLLOUT:

                    sock.on_write()
                    # I'm done with sending for now
                    if len(sock.data_to_send) == 0 and len(sock.priority_queue) == 0:
                        self.epoll.modify(sock.fileno(), RO)

            except SocketFailed:
                self.epoll.unregister(fd)
                del self.fd_to_sock[fd]
                sock.on_fail()
                self.noshot(sock)
                sock.close()

    def noshot(self, sock):
        """
        Clear all one-shots for a socket
        :param sock: BaseSocket instance
        """
        fd = sock.fileno()
        self.time_events = [q for q in self.time_events if q[1] != fd]

    def shutdown(self):
        """
        Forcibly close all sockets that this manages (calling their on_fail's),
        and close the object.

        This object is unusable after this call.
        """
        self.time_events = []
        for sock in list(six.itervalues(self.fd_to_sock)):
            sock.on_fail()
            sock.close()

        self.fd_to_sock = {}
        self.epoll.close()

    def oneshot(self, sock, delta, callback):
        """
        A socket registers a time callback
        :param sock: BaseSocket instance
        :param delta: "this seconds after now"
        :param callback: callable/0
        """
        if sock.fileno() in self.fd_to_sock:
            heapq.heappush(self.time_events, (monotonic.monotonic() + delta,
                                              sock.fileno(),
                                              callback
                                              ))

    def register(self, sock, on_read=lambda data: None,
                             on_fail=lambda: None):
        """
        Add a socket to be listened for by the loop.

        :param sock: a socket instance (as returned by socket module)
        :param on_read: callable(data) to be called with received data
        :param on_fail: callable() to be called when socket fails

        :return: a BaseSocket instance to use instead of this socket
        """
        sock = EpollSocket(sock, on_read, on_fail, self)
        self.fd_to_sock[sock.fileno()] = sock

        self.epoll.register(sock, RW)
        return sock

