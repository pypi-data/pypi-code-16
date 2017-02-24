import functools
import threading

events = []


class Event:
    """
    Simple event system.

    Usage:
        Create event
        >>> event = Event()
        Subscribe for event
            a) use increment
                >>> event += foo
            b) use method 'subscribe'
                >>> event.subscribe(foo)
        Trigger event:
            a) Call event
                >>> event()
            b) Use 'trigger' method
                >>> event.trigger()
        Unsubscribing from event:
            a) use decrement
                >>> event -= foo
            b) use method 'unsubscribe'
                >>> event.unsubscribe(foo)
    """

    def __init__(self, name=None, reverse=False, threaded=True, daemonic=True):
        """
        Register event.

        :param name: Name of event
        :type name: str
        :param reverse: call handlers from end's of list
        :param threaded: use threading
        """
        # Name
        self.name = name or "Event at " + str(hex(id(self)))

        # Settings
        self.reverse = reverse
        self.threaded = threaded
        self.daemonic = daemonic

        # Counters
        self.triggered = 0
        self.triggered_handlers = 0

        # Handlers
        self.__handlers = []

        events.append(self)

    def subscribe(self, handler: callable):
        """
        Subscribe for event
        :param handler: Callback
        :type handler: callable
        :return: Event
        """
        if handler in self.__handlers:
            raise RuntimeError(f"'{handler.__module__}.{handler.__name__}' is already subscribed for '{self}'")
        if not callable(handler):
            raise TypeError(f"'{handler.__module__}.{handler.__name__}' is not callable!")

        self.__handlers.append(handler)
        return self

    def unsubscribe(self, handler: callable):
        """
        Unsubscribe from event
        Usage
        :param handler: Callback
        :type handler: callable
        :return: Event
        """
        if handler not in self.__handlers:
            raise RuntimeError(f"'{handler.__module__}.{handler.__name__}' is already un-subscribed for '{self}'")
        self.__handlers.remove(handler)
        return self

    def get_handlers(self):
        """
        Get all handlers of event
        :return: generator
        """
        if self.reverse:
            yield from reversed(self.__handlers)
        else:
            yield from self.__handlers

    def trigger(self, *args, **kwargs):
        """
        Call all handlers
        :param args:
        :param kwargs:
        :return:
        """
        for handler in self.get_handlers():
            self._call_handler(handler, args, kwargs)
            self.triggered_handlers += 1
        self.triggered += 1

    def _call_handler(self, handler, args, kwargs):
        thread = threading.Thread(target=handler, args=args, kwargs=kwargs,
                                  name=f"{self}::{handler.__module__}.{handler.__name__}")
        thread.setDaemon(self.daemonic)
        # handler.__event__ = self
        # handler.__thread__ = thread

        thread.start()
        if not self.threaded:
            thread.join()

    def __iadd__(self, handler):
        """
        Alias for Event.subscribe(handler)
        :param handler:
        :return:
        """
        return self.subscribe(handler)

    def __isub__(self, handler):
        """
        Alias for event.unsubscribe(handler)
        :param handler:
        :return:
        """
        return self.unsubscribe(handler)

    def __call__(self, *args, **kwargs):
        """
        Alias for Event.trigger(*args, **kwargs)
        :param args:
        :param kwargs:
        :return:
        """
        return self.trigger(*args, **kwargs)

    def __len__(self):
        """
        Count of handlers
        :return:
        """
        return len(self.__handlers)

    def __del__(self):
        """
        Remove event
        :return:
        """
        events.remove(self)

    def __enter__(self):
        """
        Enter point for context manager
        :return:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit point for context manager
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        return self

    def __str__(self):
        return f"Event: {self.name}"

    def __repr__(self):
        return "<" + str(self) + " with " + str(len(self)) + " handlers>"


def event_trigger(event):
    """
    Decorator for triggering event
    usage:
        >>> foobar_event = Event(name='FooBar')
        >>> @event_trigger(foobar_event)
        >>> def trigger():
        >>>     # do something here
        >>>
        >>> trigger()
    :param event:
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            event(result, args, kwargs)
            return result

        return wrapper

    return decorator


def event_handler(event):
    """
    Decorator for triggering event
    usage:
        >>> foobar_event = Event(name='FooBar')
        >>> @event_trigger(foobar_event)
        >>> def trigger():
        >>>     # do something here
        >>>
        >>> trigger()
    :param event:
    :return:
    """

    def decorator(func):
        event.subscribe(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            event(result, args, kwargs)
            return result

        return wrapper

    return decorator
