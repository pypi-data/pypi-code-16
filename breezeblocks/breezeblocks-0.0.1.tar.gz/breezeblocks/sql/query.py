from .query_components import TableExpression
from .query_components import Referenceable
from .query_components import Selectable

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
        self._group_exprs = []
        self._having_conditions = []
        self._ordering_exprs = []
        
        self._stmt = None
        self._stmt_params = None
        self._return_type = None
        
        self.select(*select_args)
    
    def select(self, *args):
        """Adds expressions to the select clause of this query.
        
        :param args: All arguments provided to the method.
          Each argument should be a selectable expression. The only other
          possible argument is a table-like argument, from which all rows
          are to be selected.
        
        :return: `self` for method chaining.
        """
        for arg in args:
            if isinstance(arg, Selectable):
                self._output_exprs.append(arg)
                self._relations.update(arg._get_tables())
            elif isinstance(arg, TableExpression):
                self._relations.add(arg)
                self._output_exprs.extend(
                    arg._get_selectables())
            else:
                raise QueryError(arg)
        
        return self
    
    def from_(self, *args):
        """Adds table expressions to the from clause of a query.
        
        :param args: All arguments provided to the method.
          Each argument must be a table or a table-like expression to be added
          to the from clause.
        
        :return: `self` for method chaining.
        """
        for arg in args:
            if isinstance(expr, TableExpression):
                self._relation.add(arg.table)
            else:
                raise QueryError(arg)
        
        return self
    
    def where(self, *args):
        """Adds conditions to the where clause of a query.
        
        :param args: All arguments provided to the method.
          Each argument should be an expression that will result in a boolean
          value when the generated SQL is executed.
        
        :return: `self` for method chaining.
        """
        for cond in args:
            if isinstance(cond, Referenceable):
                self._where_conditions.append(cond)
                self._relations.update(cond._get_tables())
            else:
                raise QueryError(cond)
        
        return self
    
    def group_by(self, *args):
        """Sets a grouping for returned records.
        
        :param args: All arguments provided to the method.
          Each argument should be a column expression by which rows in the
          output expression can be grouped.
         
        :return: `self` for method chaining.
        """
        for arg in args:
            if isinstance(arg, Referenceable):
                self._group_exprs.append(arg)
            else:
                raise QueryError(cond)
        
        return self
    
    def having(self, *args):
        """Adds conditions to the HAVING clause of a query.
        
        Used for filtering conditions that should be applied after grouping.
        
        :param args: All arguments provided to the method.
          Each argument should be an expression that will result in a boolean
          value when the generated SQL is executed.
        
        :return: `self` for method chaining.
        """
        for cond in args:
            if isinstance(arg, Referenceable):
                self._having_conditions.append(cond)
            else:
                raise QueryError(cond)
        
        return self
    
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
        
        # Construct the 'SELECT' portion.
        query_buffer.write('SELECT\n\t')
        query_buffer.write(
            ',\n\t'.join(
                e._get_select_field() for e in self._output_exprs))
        for expr in self._output_exprs:
            self._stmt_params.extend(expr._get_params())
        
        # Construct the 'FROM' portion.
        query_buffer.write('\nFROM\n\t')
        query_buffer.write(
            ',\n\t'.join(
                t._get_from_field() for t in self._relations))
        
        # Construct the 'WHERE' portion, if used.
        if len(self._where_conditions) > 0:
            query_buffer.write('\nWHERE ')
            query_buffer.write(
                '\n  AND '.join(
                    cond._get_ref_field() for cond in self._where_conditions))
            for cond in self._where_conditions:
                self._stmt_params.extend(cond._get_params())
        
        # Construct the 'GROUP BY' portion, if used.
        if len(self._group_exprs) > 0:
            query_buffer.write('\nGROUP BY\n\t')
            query_buffer.write(
                ',\n\t'.join(
                    expr._get_ref_field() for expr in self._group_exprs))
        
        # Construct the 'HAVING' portion, if used.
        if len(self._having_conditions) > 0:
            query_buffer.write('\nHAVING ')
            query_buffer.write(
                '\n   AND '.join(
                    cond._get_ref_field() for cond in self._having_conditions))
            for cond in self._having_conditions:
                self._stmt_params.extend(cond._get_params())
        
        # Assign the resulting statement to the statement member.
        self._stmt = query_buffer.getvalue()
    
    def _construct_return_type(self):
        from collections import namedtuple
        
        fields = (f._get_name() for f in self._output_exprs)
        
        self._return_type = namedtuple('QueryResult_'+str(id(self)), fields, rename=True)
    
    def _process_result(self, r):
        return self._return_type._make(r)
    
    def execute(self):
        """Build and execute this query with the fields provided."""
        self._construct_sql()
        self._construct_return_type()
        results = []
        
        with self._db.pool.get() as conn,\
                conn.cursor() as cur:
            cur.execute(self._stmt, tuple(self._stmt_params))
            results = cur.fetchall()
        
        return [ self._process_result(r) for r in results ]
    
    def show(self):
        """Show the constructed SQL statement for this query."""
        self._construct_sql()
        
        print(self._stmt)
        print(self._stmt_params)
