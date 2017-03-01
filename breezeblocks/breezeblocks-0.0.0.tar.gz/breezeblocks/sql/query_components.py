"""Collections of classes representing specific parts of a SQL Query.

The classes defined here do not provide functionality, but are used for
typechecking in the `Query` class.

The methods they present are the methods required for them to be used in
the correct parts of the query, but raise runtime errors if not overridden.
In this way these classes also serve as a reference.
"""

class TableExpression(object):
    """Any object that can be used as a from field in a SQL query."""
    
    def _get_from_field(self):
        """Should return a string to represent the table in the from clause."""
        raise NotImplementedError()
    
    def _get_selectables(self):
        """Should return an iterable of the column expressions in this table."""
        raise NotImplementedError()

class Referenceable(object):
    """An object that can be used as a reference field in a SQL query."""
    
    def _get_ref_field(self):
        """Should return a string describing this field.
        
        May be used in the WHERE, HAVING, or GROUP BY portions of a query.
        """
        raise NotImplementedError()
    
    def _get_params(self):
        """Should return an iterable of all parameters for the query."""
        raise NotImplementedError()
    
    def _get_tables(self):
        """Should return an iterable of all tables required by this."""
        raise NotImplementedError()

class Selectable(object):
    """An object that can be used as a select field in a SQL query."""
    
    def _get_select_field(self):
        """Should return a string describing this item for the select clause."""
        raise NotImplementedError()
    
    def _get_params(self):
        """Should return an iterable of all parameters for the query."""
        raise NotImplementedError()
    
    def _get_tables(self):
        """Should return an iterable of all tables required by this."""
        raise NotImplementedError()
