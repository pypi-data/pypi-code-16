"""Provides a column class and an expression for using columns in queries."""
from .expressions import _Expr

class _ColumnBase(object):
    """A class that marks subclasses as representing database columns.
    
    This should means it is safe to construct column expressions
    from them, and will allow a :class:`Query` to do so.
    """
    def __init__(object):
        raise NotImplementedError()
    
    def expr(self):
        """Should return a :class:`ColumnExpr`.
        
        Needs to be implemented in derived classes.
        """
        raise NotImplementedError()
    
    def as_(self):
        """Should return a :class:`AliasedColumn`.
        
        Needs to be implemented in derived classes.
        """
        raise NotImplementedError()

class Column(_ColumnBase):
    """Represents a database column."""
    def __init__(self, name, table):
        """Initializes a column.
        
        :param name: The name of this column.
        
        :param table: The table to which this column belongs.
        """
        self.name = name
        
        self.table = table
        self.full_name = '.'.join([table.name, self.name])
    
    def __hash__(self):
        """Hashing is done on the qualifed name of columns.
        
        full_name := [schema_name '.'] table_name '.' column_name
        """
        return hash(self.full_name)
    
    def __eq__(self, other):
        """Tests for equality between two columns.
        
        :param other: An object to compare against this column.
          If it is another column, their full names will be compared.
          If not, this always returns false.
        """
        if isinstance(other, Column):
            return self.full_name == other.full_name
        else:
            return False
    
    def as_(self, alias):
        """Returns an aliased column referencing this column.
        
        :param alias: The string alias to be used.
        """
        return AliasedColumn(alias, self)
    
    def expr(self):
        """Returns a column expression for use in queries."""
        return ColumnExpr(self)

class AliasedColumn(_ColumnBase):
    """A column with an alias used in querying."""
    def __init__(self, alias, column):
        """Initializes an aliased column from an existing column.
        
        :param alias: The alias that will be assigned to this object.
        
        :param column: The :class:`Column` that this is going to reference.
        """
        self.column = column
        self.name = alias
    
    @property
    def table(self):
        """Returns the table of the underlying column."""
        return self.column.table
    
    @property
    def full_name(self):
        """Returns the full name of the underlying column."""
        return self.column.full_name
    
    def __eq__(self, other):
        """Tests for equality between two aliased columns.
        
        :param other: If `other` is not an aliased column, returns false.
          If it is, compares the underlying column and the alias name.
        """
        if isinstance(other, AliasedColumn):
            return self.column == other.column and self.name == other.name
        else:
            return False
    
    def expr(self):
        """Returns a column element for this column."""
        return ColumnExpr(self)
    
    def as_(self, alias):
        """Provides a different alias for the same underlying column.
        
        :param alias: Another alias to use.
        """
        return AliasedColumn(alias, self.column)

class ColumnExpr(_Expr):
    """Expression referencing a single column, aliased or unaliased."""
    def __init__(self, col):
        """Initializes a column expression.
        
        :param col: The underlying column.
        """
        self._col = col
        self.name = col.name
    
    def ref_field(self):
        """Returns a way to reference this column in a query."""
        return self._col.full_name
    
    def select_field(self):
        """Returns the expression for selecting this column in a query."""
        return '{} AS {}'.format(
            self._col.full_name, self._col.name)
