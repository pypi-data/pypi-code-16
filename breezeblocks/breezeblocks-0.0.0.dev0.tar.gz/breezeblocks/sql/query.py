from .table import _TableExpr
from .column import _ColumnBase, ColumnExpr

from .abc import Queryable

class QueryError(Exception):
    def __init__(self, value):
        self._value = value

class Query(object):
    """Represents a database query."""
    
    def __init__(self, db=None, *select_args):
        """Creates a query from a list of relations and fields.
        
        Relations should be valid table expressions.
        From a relation, all fields will be selected.
        
        Fields should be valid value expressions.
        
        :param db: A database object that connections can be gotten from.
        
        :param select_args: Any remaining arguments are consumed and
          passed to :meth:`select` for processing.
        """
        
        if db is None:
            raise QueryError('Attempting to query without a database.')
        
        self._db = db
        
        self._relations = set()
        self._output_exprs = []
        self._where_conditions = []
        self._ordering_fields = []
        
        self._stmt = None
        self._stmt_params = None
        self._return_type = None
        
        self.select(*select_args)
    
    def select(self, *args):
        for arg in args:
            if isinstance(arg, ColumnExpr):
                self._output_exprs.append(arg)
                self._relations.append(self._col.table)
            elif isinstance(arg, Queryable):
                self._output_exprs.append(arg)
            elif isinstance(arg, _ColumnBase):
                self._output_exprs.append(ColumnExpr(arg))
                self._relations.add(arg.table)
            elif isinstance(arg, _TableExpr):
                for col in arg._columns:
                    self._output_exprs.append(ColumnExpr(col))
                self._relations.add(arg)
            else:
                raise QueryError(arg)
        
        return self
    
    def from_(self, *args):
        for arg in args:
            if isinstance(expr, _TableExpr):
                self._relation.add(arg.table)
            else:
                raise QueryError(arg)
        
        return self
    
    def where(self, *args):
        """Adds condition to the where clause of a query.
        
        Returns `self` for method chaining.
        """
        for cond in args:
            if isinstance(cond, Queryable):
                self._where_conditions.append(cond)
            else:
                raise QueryError(cond)
        
        return self
    
    # TODO
    def sort(self, *args):
        """Adds a sorting column to results from the query.
        
        Also could be known as order_by.
        """
        raise NotImplementedError()
    
    # TODO
    def group_by(self, *args):
        """Sets a grouping for returned records."""
        raise NotImplementedError()
    
    # TODO
    def having(self, *args):
        raise NotImplementedError()
    
    # TODO
    def order_by(self, *args):
        raise NotImplementedError()
    
    def _construct_sql(self):
        """Constructs the resulting query string of this object.
        
        Uses `io.StringIO` as a buffer to write the query into.
        """
        from io import StringIO
        
        query_buffer = StringIO()
        self._stmt_params = []
        
        # Construct the 'SELECT' portion
        query_buffer.write('SELECT\n\t')
        query_buffer.write(
            ',\n\t'.join(
                e.select_field() for e in self._output_exprs))
        for expr in self._output_exprs:
            self._stmt_params.extend(expr.get_params())
        
        # Construct the 'FROM' portion
        query_buffer.write('\nFROM\n\t')
        query_buffer.write(
            ',\n\t'.join(
                t.from_field() for t in self._relations))
        
        # Construct the 'WHERE' portion, if used
        if len(self._where_conditions) > 0:
            query_buffer.write('\nWHERE ')
            query_buffer.write(
                '\n  AND '.join(
                    cond.ref_field() for cond in self._where_conditions))
            for cond in self._where_conditions:
                self._stmt_params.extend(cond.get_params())
        
        self._stmt = query_buffer.getvalue()
    
    def _construct_return_type(self):
        from collections import namedtuple
        
        fields = (f.name for f in self._output_exprs)
        
        self._return_type = namedtuple('QueryResult_'+str(id(self)), fields, rename=True)
    
    def _process_result(self, r):
        return self._return_type._make(r)
    
    def execute(self):
        self._construct_sql()
        self._construct_return_type()
        results = []
        
        with self._db.pool.get() as conn,\
                conn.cursor() as cur:
            cur.execute(self._stmt, tuple(self._stmt_params))
            results = cur.fetchall()
        
        return [ self._process_result(r) for r in results ]
    
    def show(self):
        self._construct_sql()
        
        print(self._stmt)
        print(self._stmt_params)
