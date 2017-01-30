import contextlib
import logging
import threading

import sqlalchemy

import chryso.errors

LOGGER = logging.getLogger(__name__)

class Transaction():
    def __init__(self, engine, parent):
        self.engine = engine
        self.parent = parent
        self.resolved = False

    @property
    def depth(self):
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth

    def savepoint(self):
        command = "SAVEPOINT chryso_{}".format(self.depth) if self.parent else "BEGIN"
        self.execute(command)
        LOGGER.debug("Executed '%s'", command)

    def rollback(self):
        if self.resolved:
            raise chryso.errors.TransactionError("This transaction is already resolved, you cannot roll it back now")
        command = "ROLLBACK TO SAVEPOINT chryso_{}".format(self.depth) if self.parent else "ROLLBACK"
        self.execute(command)
        LOGGER.debug("Executed '%s'", command)
        self.resolved = True

    def commit(self):
        if self.resolved:
            raise chryso.errors.TransactionError("This transaction is already resolved, you cannot commit it now")
        command = "RELEASE SAVEPOINT chryso_{}".format(self.depth) if self.parent else "COMMIT"
        self.execute(command)
        LOGGER.debug("Executed '%s'", command)
        self.resolved = True

    def execute(self, *args, **kwargs):
        try:
            result = self.engine.execute(*args, **kwargs)
            return result
        except (sqlalchemy.exc.DBAPIError, sqlalchemy.exc.StatementError) as e:
            raise chryso.errors.parse_exception(e)

class SemaphoreReentrant(): # pylint:disable=too-few-public-methods
    def __init__(self):
        self.lock = threading.BoundedSemaphore()
        self.thread = None
        self.entries = 0

    def __enter__(self):
        current_thread = threading.current_thread()
        if self.thread == current_thread:
            self.entries += 1
            return
        self.lock.acquire()
        self.thread = current_thread

    def __exit__(self, t, v, tb):
        if self.entries == 0:
            self.lock.release()
        else:
            self.entries -= 1


class Engine():
    def __init__(self, uri, tables, track_queries=False, echo=False, set_timezone=True):
        self._engine       = sqlalchemy.create_engine(
            uri,
            echo=echo,
            isolation_level='AUTOCOMMIT',
            pool_recycle=3600,
        )
        self.atomic_lock    = SemaphoreReentrant()
        self.queries        = []
        self.tables         = tables
        self.track_queries  = track_queries
        self.transactions   = []

        if track_queries:
            # pylint: disable=unused-variable
            @sqlalchemy.event.listens_for(self._engine, 'before_execute')
            def receive_execute(conn, clauseelement, multiparams, params): # pylint: disable=unused-argument
                self.queries.append(clauseelement)

        if set_timezone:
            # pylint: disable=unused-variable
            @sqlalchemy.event.listens_for(sqlalchemy.pool.Pool, 'connect')
            def set_utc(dbapi, record): # pylint: disable=unused-argument
                cursor = dbapi.cursor()
                cursor.execute('SET TIME ZONE UTC')
                cursor.close()

    def create_all(self):
        LOGGER.debug("Creating all tables")
        self.tables.metadata.create_all(self._engine)
        LOGGER.debug("DB tables created")

    def drop_all(self):
        LOGGER.debug("Dropping all database tables")
        self.tables.metadata.drop_all(self._engine)
        LOGGER.debug("All database tables dropped")

    def execute(self, query, *args, **kwargs):
        try:
            return self._engine.execute(query, *args, **kwargs)
        except (sqlalchemy.exc.DBAPIError, sqlalchemy.exc.StatementError) as e:
            raise chryso.errors.parse_exception(e)

    @contextlib.contextmanager
    def atomic(self):
        """
        Transaction context manager.

        Will commit the transaction on successful completion of the block or roll it back on error

        Supports nested usage (via savepoints)
        """
        with self.atomic_lock:
            parent = self.transactions[-1] if self.transactions else None
            transaction = Transaction(self, parent)
            self.transactions.append(transaction)
            transaction.savepoint()

            try:
                yield transaction
            except:
                transaction.rollback()
                raise
            else:
                if not transaction.resolved:
                    transaction.commit()
            finally:
                self.transactions.pop()

    def reset(self):
        self.drop_all()
        self.create_all()
        self.reset_queries()

    def reset_queries(self):
        self.queries = []

def store(engine):
    store.engine = engine
store.engine = None

def get():
    return store.engine
