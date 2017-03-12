from ea.lib.datastructures import DTO
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine


class EngineManager:

    def __init__(self, engines):
        self.engines = DTO(engines).as_dto()

    def engine(self, name):
        e = self.engines[name]
        if not e.get('engine'):
            e.engine = create_engine(e.dsn)
        return e.engine

    def factory(self, name):
        """Return the session factory for engine `name`."""
        e = self.engines[name]
        if not e.get('factory'):
            e.factory = scoped_session(sessionmaker(bind=e.engine))
        return e.factory

    def setup(self):
        """Create the engine for all specified data sources."""
        for e in self.engines.values():
            e.engine = create_engine(e.dsn)

    def remove(self):
        """Remove all session factories from the local scope."""
        for e in self.engines.values():
            try:
                e.pop('factory').remove()
            except KeyError:
                continue

    def teardown(self):
        """Dispose all engines."""
        for e in self.engines.values():
            if not e.get('engine'):
                continue
            e.dispose()


class TestEngineManager(EngineManager):

    def __init__(self, engines):
        self.engines = DTO(engines).as_dto()

    def factory(self, name):
        """Return the session factory for engine `name`."""
        return self.engines[name].factory

    def setup(self):
        """Set up a connection, begin a transaction and create a
        session factory for all engines.
        """
        for e in self.engines.values():
            assert 'engine' not in e
            assert 'connection' not in e
            assert 'transaction' not in e
            assert 'factory' not in e
            e.engine = create_engine(e.dsn)
            e.connection = e.engine.connect()
            e.transaction = e.connection.begin()
            e.factory = Session(e.connection)

    def teardown(self):
        """Teardown all database engines."""
        for e in self.engines.values():
            e.pop('transaction').rollback()
            e.pop('connection').close()
            e.pop('engine').dispose()

    def remove(self):
        pass
