from .column import Column

class _TableExpr(object):
    """A table expression for use in BreezeBlocks queries."""
    def __init__(self):
        raise NotImplementedError()
    
    def from_field(self):
        raise NotImplementedError()

class Table(_TableExpr):
    """Represents a database table."""
    def __init__(self, table_name, column_names, schema=None):
        """Initializes a table."""
        self._table_name = table_name
        self._schema = schema
        
        # Construct table's qualified name
        if schema is not None:
            self.name = '.'.join([schema, table_name])
        else:
            self.name = table_name
        
        # Set up columns on this table
        self.columns = {}
        self._columns = tuple()
        
        if column_names is not None:
            _columns = []
            for col_name in column_names:
                col = Column(col_name, self)
                self.columns[col_name] = col
                _columns.append(col)
            self._columns = tuple(_columns)
    
    def __hash__(self):
        """Hashing is done on the qualified name of tables.
        
        qualifed_name := [schema_name '.'] table_name
        """
        return hash(self.name)
    
    def __eq__(self, other):
        """Checks for equality with another table.
        
        If this other object is not another table, this returns false.
        Tables are only compared by qualifed name.
        """
        if isinstance(other, Table):
            return self.name == other.name
        else:
            return False
    
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.columns[key]
        else:
            raise TypeError('Tables require strings for lookup keys.')
    
    def from_field(self):
        return self.name
    
    def as_(self, alias):
        return AliasedTable(self, alias)

class AliasedTable(_TableExpr):
    """A table that has been given an alias for use in queries."""
    def __init__(self, table, alias):
        """Initializes an aliased table from a table and an alias."""
        self.table = table
        self.name = alias
        
        self.columns = {}
        
        _columns = []
        for orig_col in table._columns:
            col = Column(orig_col.name, self)
            _columns.append(col)
            self.columns[col.name] = col
            
        self._columns = tuple(_columns)
    
    def __hash__(self):
        return hash((self.name, self.table))
    
    def __eq__(self, other):
        if isinstance(other, AliasedTable):
            return self.name == other.name and self.table == other.table
        else:
            return False
    
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.columns[key]
        else:
            raise TypeError('Tables require strings for lookup keys.')
    
    def from_field(self):
        """Returns the appropriate from field for queries.
        
        This field includes both the table's original from field and the
        new alias.
        """
        return '{} AS {}'.format(
            self.table.name, self.name)
