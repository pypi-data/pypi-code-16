"""Common ZeroMQ functionality.

Processes which communicate via ZeroMQ have often a loop which
processes incoming messages, known as the poll loop.  Writing this
poll loop over and over again is rather intricate and it is easy to
get things wrong, which is why this module provides an abstraction by
reading messages from sockets using an iterator.

There are two iterators provided :class:`EventStream` and
:class:`MessageStream`.  The :class:`EventStream` is the lower-level
one which allows reacting to raw ZeroMQ POLLIN and POLLOUT events as
well as some more.  However most applications will want to use the
higher-level :class:`MessageStream` which treats everything as an
incoming message.  The two main limitations for the
:class:`MessageStream` are:

- You can not tell which socket received a message.  Usually this is
  fine as you can deduce from the message itself how it should be
  handled.

- You can not know when a socket becomes available for sending.  Some
  ZeroMQ sockets block when the outgoing queue is full, which is a
  form of back pressure.  In this case your whole thread will block
  which may not be desirable.  For some cases simply making the socket
  non-blocking and catching the :class:`zmq.Again` exception is
  sufficient.  But if good control over this behaviour is required the
  :class:`EventStream` needs to be used.
"""

import abc
import collections
import enum
import heapq
import time
import warnings

import dns.resolver
import dns.exception
import dns.rdatatype
import dns.rdataclass
import zmq
import logbook


log = logbook.Logger(__name__)


def new_context(*args, **kwargs):
    """Create a new ZeroMQ context with sensible defaults set.

    This creates a new ZeroMQ context with some default socket options
    set:

    :IPV6: We always want sockets to support IPv6 by default.

    :LINGER=300: Setting a default linger period means that when an
       unexpected exception occurs there is a better chance of being
       able to terminate the context instead of hanging forever.  The
       sockets should be garbage collected at which point they are
       closed and this default linger period will allow close to
       succeed.
    """
    ctx = zmq.Context(*args, **kwargs)
    ctx.IPV6 = True
    ctx.LINGER = 300
    return ctx


class StreamEvents(enum.IntEnum):
    """Events which can occur in an :class:`EventStream`.

    This is an enum of events returned by an eventstream:

    :POLLIN: The socket has a message queued to be received.
    :POLLOUT: The socket has space for a message it's outgoing queue.
    :TIMER: The timer has expired.

    The POLLIN and POLLOUT enumerations match the ``zmq.POLLIN`` and
    ``zmq.POLLOUT`` constants and these can be used interchangeable if
    comparison using ``==`` is used.
    """
    # The original events is a bitmask of a short in zmq_poll(3), so
    # avoid power of 2 for our own events.
    POLLIN = zmq.POLLIN
    POLLOUT = zmq.POLLOUT
    TIMER = 100


class DNSDiscoveredStreamEvents(enum.IntEnum):
    """Events which can occur in an :class:`DNSDiscoveredStream`.

    This is an enum of events returned by an DNS discovered stream:

    :POLLIN: The socket has a message queued to be received.
    :POLLOUT: The socket has space for a message it's outgoing queue.
    :FOUND: A new connection has been established.
    :LOST: A connection has been lost.

    The POLLIN and POLLOUT enumerations match the ``zmq.POLLIN`` and
    ``zmq.POLLOUT`` constants and these can be used interchangeable if
    comparison using ``==`` is used.
    """
    # The original events is a bitmask of a short in zmq_poll(3), so
    # avoid power of 2 for our own events.
    POLLIN = zmq.POLLIN
    POLLOUT = zmq.POLLOUT
    FOUND = 101
    LOST = 102


class TimerABC(metaclass=abc.ABCMeta):
    """The interface for timers used in streams.

    All timers created by a stream must implement this interface.
    interface allows the timer to say whether it is scheduled and if
    so, when it is due.  A scheduled or active timer provides the
    duration after which the timer will expire in the :attr:`when`
    attribute and is also sortable using this attribute with other
    timers.  However a timer can never be equal to another timer, only
    to itself.

    All times handled by the timer are always **relative** and in
    miliseconds.

    It is recommended for timers to sub-class this base as it
    automatically implements the sorting and hashing requirements as
    well as providing a handy monotonic timer with the correct
    milisecod resolution.
    """

    @abc.abstractproperty
    def active(self):
        """Boolean on whether the timer is currently running.

        A timer is active when it is currently scheduled and counting
        down to it's expiry time or when it has reached it's expiry
        time but has not yet been yielded by the stream.
        """

    @abc.abstractproperty
    def when(self):
        """The duration in miliseconds until the timer expires.

        The timer expires when this has reached 0.  However to keep
        timers ordered even after they are expired but before they are
        fired by the stream, this must continue counting down to
        negative values once expired.

        :raises ValueError: When the timer is not currently armed
        """

    @abc.abstractmethod
    def cancel(self):
        """Cancel the timer.

        Once called the timer is no longer active.  This is called
        automatically by the stream when the timer is yielded by the
        iterator.  If it is called by the user before the timer
        expired, or before it is yielded by the stream iterator, then
        the same effect happens and the timer will no longer be
        active.
        """

    @staticmethod
    def _time():
        """An integer monotonic time with milisecond resolution.

        This is provided as a convenience for subclasses so they do
        not have to re-invent a clock like this all the time.
        """
        return int(time.monotonic() * 1000)

    def __eq__(self, other):
        if not isinstance(other, TimerABC):
            return NotImplemented
        return self is other

    def __ne__(self, other):
        if not isinstance(other, TimerABC):
            return NotImplemented
        return self is not other

    def __cmpnums(self, other):
        """Return two numbers which can be used to compare both timers.

        This takes into account that inactive timers should sort later
        then active timers.
        """
        if not self.active and not other.active:
            return 0, 0
        elif not self.active:
            return other.when + 1, other.when
        elif not other.active:
            return self.when, self.when + 1
        else:
            return self.when, other.when

    def __lt__(self, other):
        if not isinstance(other, TimerABC):
            return NotImplemented
        num_self, num_other = self.__cmpnums(other)
        return num_self < num_other

    def __le__(self, other):
        if not isinstance(other, TimerABC):
            return NotImplemented
        num_self, num_other = self.__cmpnums(other)
        return num_self <= num_other

    def __gt__(self, other):
        if not isinstance(other, TimerABC):
            return NotImplemented
        num_self, num_other = self.__cmpnums(other)
        return num_self > num_other

    def __ge__(self, other):
        if not isinstance(other, TimerABC):
            return NotImplemented
        num_self, num_other = self.__cmpnums(other)
        return num_self >= num_other

    def __hash__(self):
        return super().__hash__()


class SimpleTimer(TimerABC):
    """A basic timer implementation for use with streams.

    This is a basic timer implementation which allows scheduling,
    re-scheduling and cancelling of the timer.  No automatic behaviour
    is implied.

    Example::
       ctx = act.zkit.new_context()
       timer = act.zkit.Timer()
       stream = act.zkit.EventStream(ctx)
       stream.register(timer, stream.TIMER)
       timer.schedule(3000)
       for msg in stream:
           assert msg is timer
           timer.schedule(3000)

    Note that timers are not thread safe and should only be
    manipulated in the same thread as the stream.
    """

    def __init__(self):
        self._deadline = None

    @property
    def active(self):
        """Whether the timer is currently scheduled."""
        return self._deadline is not None

    @property
    def when(self):
        """The number of miliseconds in which the timer will expire.

        The timer is expired when this becomes zero or smaller.

        :raises ValueError: When the timer is not currently scheduled.
        """
        if self._deadline is None:
            raise ValueError('Timer not scheduled')
        return self._deadline - self._time()

    def cancel(self):
        """Cancel the timer.

        This will unconditionally cancel the timer, whether or not it
        was scheduled.
        """
        self._deadline = None

    def schedule(self, delay):
        """Schedule the timer to expire after a number of miliseconds.

        If the timer was already scheduled the expiry time will be
        updated to the new one given.

        :param delay: The number of miliseconds after which the timer
           will expire.
        :type delay: int
        """
        self._deadline = self._time() + delay


class EventStream:
    """Abstraction to wrap around a poll loop which can be terminated.

    This is an iterable which will yield pairs of ``(item, event)``
    like a :class:`zmq.Poller` would.  But it is wrapped as an
    infinite iterator which will terminate only when :meth:`term` is
    called.  This takes care of the common details of constructing a
    poll loop.

    Additionally it supports both sockets as well as timers.  Timers
    need to be a (virtual) subclass of the :class:`TimerABC` abstract
    base class which describes how timers signal their readyness.

    This consumes the ``inproc://eventstream/*`` namespace for
    endpoints in the context.  Multiple instances will not conflict.

    It is important to call :meth:`close` when an exception occurs
    before the stream is terminated using :met:`send_term` as
    otherwise some internal resources and sockets will not be cleaned
    up and the ZeroMQ context can not be terminated.  This can be done
    with a ``try...finally`` block or :class:`contextlib.closing` but
    since you are likely to want to close sockets and other things at
    the same time another convenient way to do this is by using a
    :class:`contextlib.ExitStack` instance::

       ctx = zmq.Context()
       stream = EventStream(ctx)
       signal.signal(signal.SIGTERM, lambda: signum, frame: stream.term())
       with contextlib.ExitStack() as stack:
           stack.callback(stream.close)
           server = ctx.socket(zmq.ROUTER)
           stack.callback(server.close, linger=0)
           server.bind('tcp://*:1234')
           stream.register(server, stream.POLLIN)
           for sock, event in stream:
               assert sock is server
               assert event == stream.POLLIN

    Note that with the exception of the :meth:`term` method this class
    is not thread-safe and should only be used in the thread it was
    created in.

    :cvar POLLIN: Event to signify the returned socket has at least
       one message queue to be received non-blockingly.  This is the
       :class:`StreamEvents.POLLIN` enum.
    :cvar POLLOUT: Event to signify the returned socket can queue up
       at least one message for sending non-blockingly.  This is the
       :class:`StreamEvents.POLLOUT` enum.
    :cvar TIMER: Event to signify an expired timer.  This is the
       :class:`StreamEvents.TIMER` enum.

    :param context: The ZeroMQ context to use.  This does not affect
       which sockets you can register, it is only used to create some
       internal communication sockets.
    :type context: zmq.Context

    :ivar zmq.Context context: The ZeroMQ context in use.

    """
    POLLIN = StreamEvents.POLLIN
    POLLOUT = StreamEvents.POLLOUT
    TIMER = StreamEvents.TIMER

    def __init__(self, context):
        self.context = context
        self._term_endpoint = 'inproc://eventstream/term/{}'.format(id(self))
        self._poller = zmq.Poller()
        comm = context.socket(zmq.DEALER)
        comm.bind(self._term_endpoint)
        self._poller.register(comm, zmq.POLLIN)
        self._poison_pill = (comm, zmq.POLLIN)
        self._queued_events = collections.deque()
        self._timers = []

    def close(self):
        """Close the stream.

        This closes the EventStream instance completely.  From now on
        any next() call will raise StopIteration and any internal
        resources have been released.  It is safe to call this
        multiple times.

        This is similar to the :meth:`term` method, but has the
        crucial difference that it can only be used in the thread of
        the stream itself.  It is useful to clean up the resources of
        the stream in cases of exceptions or such, which would
        otherwise keep open sockets on the ZeroMQ context making it in
        turn impossible to terminate the context::

           ctx = zmq.Context()
           stream = act.zkit.EventStream(ctx)
           try:
               ...
               for item, event in stream:
                   ...
            finally:
               stream.close()
        """
        if not self.closed:
            self._queued_events.appendleft(self._poison_pill)
            comm = self._poison_pill[0]
            if not comm.closed:
                comm.close(linger=0)

    def __del__(self):
        self.close()

    @property
    def closed(self):
        """Boolean indicating whether the stream is closed.

        The stream can be closed by calling :meth:`send_term` or
        :meth:`close`, after which it can no longer be used.
        """
        try:
            evt = self._queued_events[0]
        except IndexError:
            return False
        else:
            return evt == self._poison_pill

    @property
    def terminated(self):
        """Deprecated alias of :attr:`closed`."""
        warnings.warn('Use the closed attribute instead', DeprecationWarning)
        return self.closed

    def register(self, item, events):
        """Add a socket or timer to the poll loop.

        :param item: The ZeroMQ socket or TimerABC instance to
           register.
        :type item: zmq.Socket or TimerABC
        :param events: A bitmask of StreamEvents items.  Note that
           when registering a timer you must use the TIMER event.
        :type events: StreamEvents

        For sockets, if the socket is already registered the
        registration will be overwritten and the new events will be
        used.  Sockets MUST be registered using only the
        :attr:`StreamEvents.POLLIN` and :attr:`StreamEvents.POLLOUT`
        events.

        For timers registering and already registered timer will have
        no effect.  Timers MUST be registered using the
        :attr:`StreamEvents.TIMER` event.

        :raises ValueError: for invalid bitmask combinations.
        """
        if events == self.TIMER:
            if item not in self._timers:
                heapq.heappush(self._timers, item)
        elif events | self.POLLIN | self.POLLOUT == self.POLLIN | self.POLLOUT:
            self._poller.register(item, events)
        else:
            raise ValueError('Invalid events bitmask')

    def unregister(self, item):
        """Remove a socket or timer from the poll loop.

        :raises LookupError: If the item is not registered.
        """
        try:
            self._timers.remove(item)
        except ValueError:
            try:
                self._poller.unregister(item)
            except KeyError as err:
                raise LookupError('Item not registerd') from err
            else:
                for sock, event in list(self._queued_events):
                    if sock == item:
                        self._queued_events.remove((sock, event))
                        break
        else:
            heapq.heapify(self._timers)

    def _next_timer(self):
        """Return the delay to the next expiring timer.

        This looks at the scheduled timers and returns the time until
        the next timer expires in miliseconds.  If there are currently
        expired timers this will return 0.  If there are not scheduled
        timers this will return ``None``.
        """
        # Timers could have changed their scheduling time, so we need
        # to re-heapify the timers priority queue.
        heapq.heapify(self._timers)
        try:
            delay = max(self._timers[0].when, 0)
        except (IndexError, ValueError):
            delay = None
        return delay

    def poll(self, timeout=None):
        """Poll for an event.

        :param int timeout: Timeout in milliseconds.

        :returns: ``True`` if an event is ready and calling ``next()``
           on the iterator will not block.  If no event is ready
           ``False`` will be returned.
        """
        if self._queued_events:
            return True
        next_timer = self._next_timer()
        if next_timer is None and timeout is None:
            poll_timeout = None
        elif next_timer is None:
            poll_timeout = max(timeout, 0)
        elif timeout is None:
            poll_timeout = next_timer
        else:
            poll_timeout = min(max(timeout, 0), next_timer)
        sock_ready = bool(self._poller.poll(poll_timeout))
        if sock_ready:
            return sock_ready
        elif self._timers and self._timers[0].active:
            return self._timers[0].when <= 0
        else:
            return False

    def __iter__(self):
        return self

    def __next__(self):
        # The need to queue events like this arises to ensure we do
        # not starve different events.  The API of the poller does not
        # guarantee that we would not starve a second socket if only
        # one was processed but it became ready again before the next
        # call.
        if not self._queued_events:
            timeout = self._next_timer()
            self._queued_events.extend(self._poller.poll(timeout))
            if timeout == 0 or not self._queued_events:
                timer = heapq.heappop(self._timers)
                timer.cancel()
                heapq.heappush(self._timers, timer)
                return (timer, self.TIMER)
        item = self._queued_events.popleft()
        if item == self._poison_pill:
            comm = item[0]
            if not comm.closed:
                comm.close(linger=0)
            self._queued_events.appendleft(item)
            raise StopIteration('Stream closed')
        return item

    def send_term(self):
        """Signal the iterator loop to terminate.

        This will result in :class:`StopIteration` being raised in the
        iterator.  This is the only method which can be safely called
        from a different thread.  Calling it multiple times is safe as
        well.
        """
        sock = self.context.socket(zmq.DEALER)
        sock.connect(self._term_endpoint)
        sock.send(b'')
        sock.close(linger=0)

    def term(self):
        """Deprecated alias for :meth:`send_term`."""
        warnings.warn('Use .send_term() instead', DeprecationWarning)
        self.send_term()


class MessageStream:
    """Abstraction to receive messages from ZeroMQ sockets.

    This is an abstraction on top of :class:`EventStream` which
    simplifies receiving messages from one or more ZeroMQ sockets.
    Its API is just a little easier to use if all you need to do is
    receive messages and you do not need to be told which socket
    received the message (or you only register one socket)::

       with contextlib.ExitStack() as stack:
           ctx = stack.enter_context(zmq.Context())
           server = ctx.socket(zmq.ROUTER)
           stack.callback(server.close, linger=0)
           server.bind('tcp://*:1234')
           stream = MessageStream(ctx)
           stack.callback(stream.close)
           stream.register(server)
           signal.signal(signal.SIGTERM, labmda: signum, frame: stream.term)
           for msg in stream:
               frame0, frame1 = msg  # this is a ZeroMQ multipart message
               assert isinstance(frame0, bytes)

    Just like for :class:`EventStream` timers can be registered as
    well.  When a timer fires the timer instance itself is yielded
    from the iterator as the message.

    Note that with the exception of the :meth:`term` method this class
    is not thread-safe and should only be used in the thread it was
    created in.

    :param zmq.Context context: The ZeroMQ context to use.  This is
       only used to create the sockets to signal the loop should
       terminate.

    :ivar zmq.Context context: The ZeroMQ context in use.
    """

    def __init__(self, context):
        self.context = context
        self._evtstream = EventStream(context)

    def __del__(self):
        self.close()

    @property
    def closed(self):
        """Boolean indicating whether the stream is closed.

        The stream is closed by calling :meth:`send_term` or
        :meth:`close`, after which it can no longer be used and
        iteration will raise :class:`StopIteration`.
        """
        return self._evtstream.closed

    @property
    def terminated(self):
        """Deprecated alias of :attr:`closed`."""
        warnings.warn('Use the closed attribute instead', DeprecationWarning)
        return self.closed

    def close(self):
        """Close the stream completely.

        This can be used to terminate the stream completely and
        release all resources in case an exception occurs during use
        rather then terminating via :meth:`term`.  You might want to
        use it with a :class:`contextlib.closing` or
        :class:`contextlib.ExitStack` instead of manually invoking it.
        """
        self._evtstream.close()

    def register(self, item):
        """Register a socket or timer to receive messages from.

        Timers are recognised by being a subclass of
        :class:`TimerABC`.
        """
        if isinstance(item, TimerABC):
            self._evtstream.register(item, StreamEvents.TIMER)
        else:
            self._evtstream.register(item, StreamEvents.POLLIN)

    def unregister(self, item):
        """Remove a socket, stopping messages being received from it."""
        self._evtstream.unregister(item)

    def poll(self, timeout=None):
        """Poll for a message.

        :param int timeout: Timeout in miliseconds.

        :returns: ``True`` if an message is ready and a calling
           ``next()`` on the iterator will not block.  If no message
           is ready ``False`` will be returned.
        """
        return self._evtstream.poll(timeout)

    def __iter__(self):
        return self

    def __next__(self):
        obj, evt = next(self._evtstream)
        if evt == EventStream.POLLIN:
            return obj.recv_multipart()
        elif evt == EventStream.TIMER:
            return obj
        else:
            raise RuntimeError('Unexpected event received')

    def send_term(self):
        """Signal the iterator loop to terminate.

        This will result in :class:`StopIteration` being raised in the
        iterator.  This is the only method which can be safely called
        from a different thread.  Calling it multiple times is safe as
        well.
        """
        self._evtstream.send_term()

    def term(self):
        """Deprecated alias for :meth:`send_term`."""
        warnings.warn('Use .send_term() instead', DeprecationWarning)
        self.send_term()


class DNSDiscoveredStream:
    """Discover ZMQ endpoints from DNS.

    Instances of this class manage pools of ZMQ sockets which are connected
    to endpoints which are discovered by periodic DNS lookups. For example,
    when a new endpoint is exposed by DNS then a socket is automatically
    created and connected to. Conversely, when an endpoint ceases to be
    present via DNS, then the corresponding socket is closed and dropped
    from the pool.

    The ZMQ context bound to the stream is used to create new sockets.
    Therefore, it is advisable to set socket options on the context it
    self so that they are inherited by the created sockets. For example,
    subscribing to multiple ZMQ publishers:

    .. code-block:: python

        context = act.zkit.new_context()
        context.SUBSCRIBE = b'...'
        stream = DNSDiscoveredStream(context, zmq.SUB, '...')
        for socket, event in stream:
            if event == DNSDiscoveredStreamEvents.POLLIN:
                message = socket.recv_multipart()

    Changing the context's socket options during iteration will only affect
    newly created sockets and hence, is strongly discouraged.

    Iterating over the stream yields two item tuples containg a socket
    with an associated event from :class:`DNSDiscoveredStreamEvents`.
    As the sockets are managed by the stream it self, consumers of the stream
    must be careful if holding onto references to the sockets, as they may be
    closed with later iterations. However, each socket is guaranteed to
    remain open for the iteration that yielded it.

    By default, the stream will perform an initial DNS lookup upon iteration
    and then query DNS at five second intervals. This interval can be
    modified via the :attr:`frequency` attribute. However, note that the DNS
    lookup will only occur upon iteration, therefore the query frequency is
    only aa approximation of how frequently DNS queries will be made.

    A :attr:`frequency` of zero will result in a DNS lookup being made for
    every iteration through stream.

    Discovering endpoints is done using a combination of a DNS label
    :attr:`name` and a :attr:`service`. The service may either be a
    symbolic name as a string or a integer port number. When a port number
    is given, the stream discovers IP addresses corresponding to the given
    DNS name.

    Conversely, when a symbolic service name, the will discover both
    the IP address *and* port number for a given endpoint. Note, that
    only TCP ports are discovered.

    name is used, the stream can discover both the IP address *and* port
    number for a given endpoint.

    :param zmq.Context context: The ZMQ context to use to create new
        sockets.
    :param socket_type: The type of ZMQ socket to create when a new
        endpoint is discovered.
    :param str name: The DNS name to periodically check for new endpoints.
    :param service: The symbolic name of the service as a DNS label or
        a numeric port number.
    :type service: str or int
    :param int frequency: How long to wait between DNS lookups in milliseconds.
    """

    def __init__(self, context, socket_type,
                 name, service, frequency=5000):
        self.context = context
        if socket_type not in {zmq.REQ, zmq.PULL, zmq.SUB}:
            raise ValueError('Can only using DNS discovered '
                             'stream with REQ, PULL and SUB sockets')
        self.socket_type = socket_type
        self.name = name
        self.service = service
        self.frequency = frequency
        self._sockets = {}  # endpoint : socket
        self._event_stream = EventStream(context)
        self._timer = SimpleTimer()
        self._timer.schedule(0)
        self._event_stream.register(self._timer, StreamEvents.TIMER)
        self._discovery_events = collections.deque()
        self._resolver = dns.resolver.Resolver()

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self._discovery_events:
                return self._discovery_events.popleft()
            else:
                object_, event = next(self._event_stream)
                if object_ is self._timer:
                    self._discovery_events.extend(self._discover())
                    self._timer.schedule(self.frequency)
                else:
                    return object_, event

    @property
    def closed(self):
        """Boolean indicating whether the stream is closed.

        The stream is closed by calling :meth:`send_term` or
        :meth:`close`, after which it can no longer be used and
        iteration will raise :class:`StopIteration`.
        """
        return self._event_stream.closed

    def close(self):
        """Close the stream completely.

        This can be used to terminate the stream completely and
        release all resources in case an exception occurs during use
        rather then terminating via :meth:`term`.  You might want to
        use it with a :class:`contextlib.closing` or
        :class:`contextlib.ExitStack` instead of manually invoking it.
        """
        try:
            self._event_stream.unregister(self._timer)
        except LookupError:
            pass  # Closed, before had chance to register
        for socket in self._sockets.values():
            socket.close(linger=0)
            self._event_stream.unregister(socket)
        self._sockets.clear()
        self._event_stream.close()

    def send_term(self):
        """Signal the iterator loop to terminate.

        This will result in :class:`StopIteration` being raised in the
        iterator.  This is the only method which can be safely called
        from a different thread.  Calling it multiple times is safe as
        well.
        """
        self._event_stream.send_term()

    def _resolve_srv(self, name, service):
        """Resolve a DNS name and service to port numbers.

        The given service may be an integer port number or a symbolic
        service name. If a port number is given, all endpoints returned
        will have the same port number.

        If a symbolic service name is given then the protocol is assumed
        to be TCP, so that the queried name is `_{service}._tcp.{name}`.
        Each SRV record returned maps onto a corresponding name -- the
        target -- which can be resolved to an A record to form the
        complete address.

        :param name: The DNS name to lookup.
        :type name: str
        :param service: The port number or symbolic service name to lookup.
        :type service: str or int

        :returns: An iterator of two-item tuples containing the port
            number as a number and corresponding DNS name, as a string,
            that should resolve to A records.
        """
        symbolic_service = isinstance(service, str)
        query = name
        if symbolic_service:
            query = \
                '_{service}._tcp.{name}'.format(name=name, service=service)
        try:
            answer = self._resolver.query(
                query, dns.rdatatype.SRV, dns.rdataclass.IN, tcp=True)
        except (dns.exception.Timeout,
                dns.resolver.NXDOMAIN, dns.resolver.NoAnswer) as exc:
            log.debug(
                'DNS lookup failed for {!r}: {}'.format(query, exc))
        else:
            for result in answer:
                port = str(result.port)
                if not symbolic_service:
                    port = str(service)
                yield port, str(result.target)

    def _resolve_a(self, name):
        """Resolve a DNS name to an A records.

        :param str name: The DNS name to lookup.

        :returns: An iterator of IPv4 addresses as strings in
            dotted-decimal notation.
        """
        try:
            answer = self._resolver.query(
                name, dns.rdatatype.A, dns.rdataclass.IN, tcp=True)
        except (dns.exception.Timeout,
                dns.resolver.NXDOMAIN, dns.resolver.NoAnswer) as exc:
            log.debug(
                'DNS lookup failed for {!r}: {}'.format(self.name, exc))
        else:
            for result in answer:
                yield result.address

    def _resolve(self):
        """Resolve DNS records into ZMQ endpoints.

        :returns: A set of ZMQ endpoints as byte-strings.
        """
        endpoints = set()
        for port, name in self._resolve_srv(self.name, self.service):
            for address in self._resolve_a(name):
                endpoints.add(
                    'tcp://{}:{}'.format(address, port).encode())
        if not endpoints:
            log.warning('Could not find any '
                        'endpoints using name {!r}', self.name)
        return endpoints

    def _discover(self):
        """Discover and connect to ZMQ endpoints.

        For newly discovered endpoints a socket of the given
        :attr:`socket_type` is created, connected and added to the
        stream's socket pool..

        The sockets for any endpoints which are no longer listed by DNS
        are closed and dropped from the stream's socket pool.

        :returns: A list of stream event tuples.
        """
        events = []
        endpoints_active = set(self._sockets.keys())
        endpoints_new = self._resolve()
        for endpoint_removed in endpoints_active - endpoints_new:
            socket = self._sockets[endpoint_removed]
            socket.close(linger=0)
            self._event_stream.unregister(socket)
            del self._sockets[endpoint_removed]
            log.info('Lost connection to {}'.format(endpoint_removed))
            events.append((socket, DNSDiscoveredStreamEvents.LOST))
        for endpoint_added in endpoints_new - endpoints_active:
            socket = self.context.socket(self.socket_type)
            socket.connect(endpoint_added)
            self._event_stream.register(socket, StreamEvents.POLLIN)
            self._sockets[endpoint_added] = socket
            log.info('Established connection to {}'.format(endpoint_added))
            events.append((socket, DNSDiscoveredStreamEvents.FOUND))
        return events
