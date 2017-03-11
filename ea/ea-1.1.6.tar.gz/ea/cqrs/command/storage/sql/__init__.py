import threading

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import ioc

from ea.cqrs.command.storage.sql.orm import Relation
from ea.cqrs.command.storage.sql.orm import Command
from ea.cqrs.command.storage.base import BaseCommandStore


class SQLCommandStore(BaseCommandStore):
    dsn = ioc.class_property('SQLCommandStore.dsn')
    storage_class = Command
    base = Relation

    @property
    def engine(self):
        if self._engine is None:
            with self._lock:
                self._engine = create_engine(self.dsn)

            # TODO: Very ugly place to do this.
            self.base.metadata.create_all(self._engine)

        return self._engine

    @property
    def session_factory(self):
        if not self._session_factory:
            with self._lock:
                Session = sessionmaker(bind=self.engine)
                self._session_factory = scoped_session(Session)

        return self._session_factory

    def __init__(self):
        self._engine = None
        self._session_factory = None
        self._lock = threading.RLock()

    def store(self, dao):
        session = self.session_factory()
        try:
            self.logger.debug("Persisting command %s", dao.id)
            session.add(dao)
            session.commit()
        except Exception as e:
            self.logger.exception("Caught fatal exception while persisting command %s", dao.id)
            session.rollback()
            raise
        finally:
            self.session_factory.remove()
