"""Kazoo handler helpers"""

import errno
import functools
import select
import time

HAS_FNCTL = True
try:
    import fcntl
except ImportError:  # pragma: nocover
    HAS_FNCTL = False

# sentinel objects
_NONE = object()


class AsyncResult(object):
    """A one-time event that stores a value or an exception"""
    def __init__(self, handler, condition_factory, timeout_factory):
        self._handler = handler
        self._exception = _NONE
        self._condition = condition_factory()
        self._callbacks = []
        self._timeout_factory = timeout_factory
        self.value = None

    def ready(self):
        """Return true if and only if it holds a value or an
        exception"""
        return self._exception is not _NONE

    def successful(self):
        """Return true if and only if it is ready and holds a value"""
        return self._exception is None

    @property
    def exception(self):
        if self._exception is not _NONE:
            return self._exception

    def set(self, value=None):
        """Store the value. Wake up the waiters."""
        with self._condition:
            self.value = value
            self._exception = None
            for callback in self._callbacks:
                self._handler.completion_queue.put(
                    lambda: callback(self)
                )
            self._condition.notify_all()

    def set_exception(self, exception):
        """Store the exception. Wake up the waiters."""
        with self._condition:
            self._exception = exception
            for callback in self._callbacks:
                self._handler.completion_queue.put(
                    lambda: callback(self)
                )
            self._condition.notify_all()

    def get(self, block=True, timeout=None):
        """Return the stored value or raise the exception.

        If there is no value raises TimeoutError.

        """
        with self._condition:
            if self._exception is not _NONE:
                if self._exception is None:
                    return self.value
                raise self._exception
            elif block:
                self._condition.wait(timeout)
                if self._exception is not _NONE:
                    if self._exception is None:
                        return self.value
                    raise self._exception

            # if we get to this point we timeout
            raise self._timeout_factory()

    def get_nowait(self):
        """Return the value or raise the exception without blocking.

        If nothing is available, raises TimeoutError

        """
        return self.get(block=False)

    def wait(self, timeout=None):
        """Block until the instance is ready."""
        with self._condition:
            self._condition.wait(timeout)
        return self._exception is not _NONE

    def rawlink(self, callback):
        """Register a callback to call when a value or an exception is
        set"""
        with self._condition:
            # Are we already set? Dispatch it now
            if self.ready():
                self._handler.completion_queue.put(
                    lambda: callback(self)
                )
                return

            if callback not in self._callbacks:
                self._callbacks.append(callback)

    def unlink(self, callback):
        """Remove the callback set by :meth:`rawlink`"""
        with self._condition:
            if self.ready():
                # Already triggered, ignore
                return

            if callback in self._callbacks:
                self._callbacks.remove(callback)


def _set_fd_cloexec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)


def _set_default_tcpsock_options(module, sock):
    sock.setsockopt(module.IPPROTO_TCP, module.TCP_NODELAY, 1)
    if HAS_FNCTL:
        _set_fd_cloexec(sock)
    return sock


def create_socket_pair(module, port=0):
    """Create socket pair.

    If socket.socketpair isn't available, we emulate it.
    """
    # See if socketpair() is available.
    have_socketpair = hasattr(module, 'socketpair')
    if have_socketpair:
        client_sock, srv_sock = module.socketpair()
        return client_sock, srv_sock

    # Create a non-blocking temporary server socket
    temp_srv_sock = module.socket()
    temp_srv_sock.setblocking(False)
    temp_srv_sock.bind(('', port))
    port = temp_srv_sock.getsockname()[1]
    temp_srv_sock.listen(1)

    # Create non-blocking client socket
    client_sock = module.socket()
    client_sock.setblocking(False)
    try:
        client_sock.connect(('localhost', port))
    except module.error as err:
        # EWOULDBLOCK is not an error, as the socket is non-blocking
        if err.errno != errno.EWOULDBLOCK:
            raise

    # Use select to wait for connect() to succeed.
    timeout = 1
    readable = select.select([temp_srv_sock], [], [], timeout)[0]
    if temp_srv_sock not in readable:
        raise Exception('Client socket not connected in %s'
                        ' second(s)' % (timeout))
    srv_sock, _ = temp_srv_sock.accept()
    return client_sock, srv_sock


def create_tcp_socket(module):
    """Create a TCP socket with the CLOEXEC flag set.
    """
    type_ = module.SOCK_STREAM
    if hasattr(module, 'SOCK_CLOEXEC'):  # pragma: nocover
        # if available, set cloexec flag during socket creation
        type_ |= module.SOCK_CLOEXEC
    sock = module.socket(module.AF_INET, type_)
    _set_default_tcpsock_options(module, sock)
    return sock


def create_tcp_connection(module, address, timeout=None):
    end = None
    if timeout is None:
        # thanks to create_connection() developers for
        # this ugliness...
        timeout = module.getdefaulttimeout()
    if timeout is not None:
        end = time.time() + timeout
    sock = None

    while end is None or time.time() < end:
        try:
            # if we got a timeout, lets ensure that we decrement the time
            # otherwise there is no timeout set and we'll call it as such
            timeout_at = end if end is None else end - time.time()
            sock = module.create_connection(address, timeout_at)
            break
        except Exception as ex:
            errnum = ex.errno if isinstance(ex, OSError) else ex[0]
            if errnum == errno.EINTR:
                continue
            raise

    if sock is None:
        raise module.error

    _set_default_tcpsock_options(module, sock)
    return sock


def capture_exceptions(async_result):
    """Return a new decorated function that propagates the exceptions of the
    wrapped function to an async_result.

    :param async_result: An async result implementing :class:`IAsyncResult`

    """
    def capture(function):
        @functools.wraps(function)
        def captured_function(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as exc:
                async_result.set_exception(exc)
        return captured_function
    return capture


def wrap(async_result):
    """Return a new decorated function that propagates the return value or
    exception of wrapped function to an async_result.  NOTE: Only propagates a
    non-None return value.

    :param async_result: An async result implementing :class:`IAsyncResult`

    """
    def capture(function):
        @capture_exceptions(async_result)
        def captured_function(*args, **kwargs):
            value = function(*args, **kwargs)
            if value is not None:
                async_result.set(value)
            return value
        return captured_function
    return capture
