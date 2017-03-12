import contextlib
import functools
import threading

import ioc


class SessionManager:
    """A mixin class that provides helper methods and attributes
    to set up and tear down a SQLAlchemy session. For use with
    :class:`Service` implementations.
    """
    engine = None
    manager = ioc.class_property('EngineManager')

    @property
    def session(self):
        return self.manager.factory(self.engine)

    @classmethod
    def with_session(cls, func):
        """Decorate a method to properly set up an tear down
        the session.
        """
        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            with self.transaction():
                return func(self, *args, **kwargs)

        return decorator

    def __init__(self, *args, **kwargs):
        super(SessionManager, self).__init__(*args, **kwargs)
        self._factory = None
        self._engine = None
        self._local = threading.local()
        self._local.session = None

    def begin(self):
        if not hasattr(self._local, 'depth'):
            self._local.depth = -1
        self._local.depth += 1
        if self._local.depth > 0:
            self.session.begin_nested()

    def commit(self):
        self.flush()
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def flush(self):
        self.session.flush()

    @contextlib.contextmanager
    def transaction(self, write=True):
        if not hasattr(self._local, 'depth'):
            self._local.depth = -1
        self.begin()
        try:
            yield
        except Exception:
            self.rollback()
            raise
        else:
            self.commit()
        finally:
            self._local.depth -= 1
