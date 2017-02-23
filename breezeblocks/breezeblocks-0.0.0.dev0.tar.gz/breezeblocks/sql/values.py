"""Defines some availble types of value expressions for DBAPI queries."""
from .expressions import ConstantExpr

class FormatStyleValue(ConstantExpr):
    """A format-style constant value expression.
    
    Placeholders in queries will appear as '%s'.
    """
    def ref_field(self):
        return '%s'
    
    def select_field(self):
        return '%s'

class PyFormatStyleValue(ConstantExpr):
    """A pyformat-style constant value expression.
    
    Placeholders in queries will appear as '%s'.
    Support for named paramaters has not been implemented.
    """
    def ref_field(self):
        return '%s'
    
    def select_field(self):
        return '%s'

class QmarkStyleValue(ConstantExpr):
    """A qmark-style constant value expression.
    
    Placeholders in queries will appear as '?'.
    """
    def ref_field(self):
        return '?'
    
    def select_field(self):
        return '?'
