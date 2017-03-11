import logging


class EventListenerMeta(type):

    def __new__(cls, name, bases, attrs):
        attrs['__wants__'] = set()
        return super(EventListenerMeta, cls)\
            .__new__(cls, name, bases, attrs)


class EventListener(metaclass=EventListenerMeta):
    """A handler that listens for one or more types of
    events.

    Events are processed in multiple stages:

    1.  :meth:`is_interested()` is invoked in order to
        determine if the listener is interested. The
        method returns a boolean.
    2.  The next method to be called is :meth:`pre_handle()`.
    3.  The third step is to invoke :meth:`handle()`. This
        is where the business logic lives.
    4.  If :meth:`handle()` returns succesfully, :meth:`post_handle()`
        is invoked.
    5.  On exceptions during any method, :meth:`on_exception()`
        is invoked receiving the exception instance, phase indicator
        (`pre_handle`,'handle' or `post_handle`) and event as
        positional arguments.

    To stop processing an event, any method may raise :meth:drop()`.
    """
    logger = logging.getLogger('eda.listener')
    Drop = type('Drop', (Exception,), {})
    event_class = None

    @classmethod
    def wants(cls, event_class):
        def decorator(cls):
            cls.__wants__.add(event_class.meta.name)
            return cls
        return decorator

    def is_interested(self, event):
        name = event.headers.type
        if self.__wants__ and name not in self.__wants__:
            return False

        dto = event.params
        if self.event_class:
            dto = self.event_class.as_dto(**dto)

        return self.can_handle(event), dto

    def can_handle(self, event):
        return bool(self.__wants__)

    def pre_handle(self, event):
        pass

    def post_handle(self, event):
        pass

    def handle(self, headers, params):
        raise NotImplementedError("Subclasses must override this method.")

    def on_exception(self, exc, phase, event):
        pass

    def drop(self):
        raise self.Drop

    def __call__(self, event):
        phase = 'pre_handle'
        try:
            self.pre_handle(event)
            phase = 'handle'
            dto = event.params
            self.handle(event.headers, dto)
            phase = 'post_handle'
            self.post_handle(event)
        except self.Drop:
            return
        except Exception as e:
            if not self.on_exception(e, phase, event):
                raise

        self.logger.info("%s finished processing event %s",
            type(self).__name__, event.headers.id)

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other):
        return type(self) == type(other)
