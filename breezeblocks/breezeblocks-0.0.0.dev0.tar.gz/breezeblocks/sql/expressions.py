"""Defines the building blocks for SQL expressions.

These classes are meant to be extended for concrete expression
classes and provide most necessary functionality.
"""
from .abc import Queryable
from . import operators as op

class _Expr(object):
    """An expression that can be used by a BreezeBlocks `Query`.
    
    Using this as a base class for query-bound expressions
    will allow them to use python operators to generate
    BreezeBlocks SQL operators.
    
    Several Built-in methods on this class do not return the
    Python-intuitive value, but an operation from operators
    that can be used in query-building.
    """
    def __init__(self):
        raise NotImplementedError()
    
    def ref_field(self):
        raise NotImplementedError()
    
    def select_field(self):
        raise NotImplementedError()
    
    def get_params(self):
        """Returns a tuple of the parameters of this expression.
        
        For most expressions this will be an empty tuple, so this
        does not need to be overridden.
        """
        return tuple()
    
    def as_(self, alias):
        """Returns an aliased version of this expression."""
        return _AliasedExpr(self, alias)
    
    # Comparisons
    def __eq__(self, other):
        return op.Equal_(self, other)
    
    def __ne__(self, other):
        return op.NotEqual_(self, other)
    
    def __lt__(self, other):
        return op.LessThan_(self, other)
    
    def __gt__(self, other):
        return op.GreaterThan_(self, other)
    
    def __le__(self, other):
        return op.LessThanEqual_(self, other)
    
    def __ge__(self, other):
        return op.GreaterThanEqual_(self, other)
    
    # Binary Arithmetic operators
    def __add__(self, other):
        return op.Plus_(self, other)
    
    def __sub__(self, other):
        return op.Minus_(self, other)
    
    def __mul__(self, other):
        return op.Mult_(self, other)
    
    def __truediv__(self, other):
        return op.Div_(self, other)
    
    def __mod__(self, other):
        return op.Mod_(self, other)
    
    def __pow__(self, other):
        return op.Exp_(self, other)
    
    # Unary Arithmetic operators
    def __pos__(self):
        return op.UnaryPlus_(self)
    
    def __neg__(self):
        return op.UnaryMinus_(self)
    
class _AliasedExpr(object):
    """An expression using an alias to change its visible name.
    
    The underlying expression can be anything deriving from
    :class:`_Expr` and providing a :meth:`ref_field` method that
    returns a string.
    """
    def __init__(self, expr, alias):
        self._expr = expr
        self.name = alias
    
    def ref_field(self):
        return self._expr.ref_field()
    
    def select_field(self):
        return '{} AS {!s}'.format(
            self._expr.ref_field(), self.name)
    
    def get_params(self):
        return self._expr.get_params()

class ConstantExpr(_Expr):
    """A constant value or literal for safe use in a query.
    
    This version of the class should not be used as it does not know
    the needed DBAPI param style. Instantiate a subclass overriding
    `__str__` instead.
    """
    def __init__(self, value):
        """Sets value equal to the provided value."""
        self._value = value
    
    def ref_field(self):
        """Implemented in derived classes.
        
        Should return a string for use in queries."""
        raise NotImplementedError()
    
    def select_field(self):
        """Implemented in derived classes.
        
        Should return a string for use in a query.
        """
        raise NotImplementedError()
    
    def get_params(self):
        return (self._value,)

Queryable.register(_Expr)
Queryable.register(_AliasedExpr)
