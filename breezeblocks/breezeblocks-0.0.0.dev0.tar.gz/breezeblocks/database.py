from .pool import ConnectionPool as Pool

from .sql.table import Table
from .sql.column import Column
from .sql.query import Query

class Database(object):
    """Proxies the database at the URI provided."""
    def __init__(self, dsn, dbapi_module=None, *args,
            minconn=10, maxconn=20, **kwargs):
        self._dsn = dsn
        self._dbapi = dbapi_module
        
        self._connection_args = args
        self._connection_kwargs = kwargs
        
        self.pool = Pool(self._dbapi, minconn, maxconn,
            dsn, *args, **kwargs)
        
        self._schemas = {}
        self._tables = {}
    
    def query(self, *queryables):
        return Query(self, *queryables)
    
    def connect(self):
        """Returns a new connection to the database.
        
        The returned connection is not from the connection pool."""
        return self._dbapi.connect(self._dsn,
            *self._connection_args, **self._connection_kwargs)
