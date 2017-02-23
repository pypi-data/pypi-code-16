"""Defines object reprentations for SQL Operators."""
from .abc import Queryable

class _OperatorExpr(object):
    """SQL operator base class that implements common methods."""
    def __init__(self):
        raise NotImplementedError()
    
    def ref_field(self):
        raise NotImplementedError()
    
    def select_field(self):
        return self.as_('_').select_field()
    
    def get_params(self):
        raise NotImplementedError()
    
    def as_(self, alias):
        return _AliasedOperatorExpr(self, alias)
    
    # Comparisons
    def __eq__(self, other):
        return Equal_(self, other)
    
    def __ne__(self, other):
        return NotEqual_(self, other)
    
    def __lt__(self, other):
        return LessThan_(self, other)
    
    def __gt__(self, other):
        return GreaterThan_(self, other)
    
    def __le__(self, other):
        return LessThanEqual_(self, other)
    
    def __ge__(self, other):
        return GreaterThanEqual_(self, other)
    
    # Binary Arithmetic operators
    def __add__(self, other):
        return Plus_(self, other)
    
    def __sub__(self, other):
        return Minus_(self, other)
    
    def __mul__(self, other):
        return Mult_(self, other)
    
    def __truediv__(self, other):
        return Div_(self, other)
    
    def __mod__(self, other):
        return Mod_(self, other)
    
    def __pow__(self, other):
        return Exp_(self, other)
    
    # Unary Arithmetic operators
    def __pos__(self):
        return UnaryPlus_(self)
    
    def __neg__(self):
        return UnaryMinus_(self)

class _AliasedOperatorExpr(object):
    def __init__(self, operator, alias):
        self._operator = operator
        self._alias = alias
    
    def ref_field(self):
        return '{}'.format(self._operator.ref_field())
    
    def select_field(self):
        return '{} AS {}'.format(
            self._operator.ref_field(), self._alias)

class _UnaryOperator(_OperatorExpr):
    """SQL Unary Operator"""
    def __init__(self, operand):
        self._operand = operand
    
    def get_params(self):
        return self._operand.get_params()

class _BinaryOperator(_OperatorExpr):
    """SQL Binary Operator"""
    def __init__(self, lhs, rhs):
        self._lhs = lhs
        self._rhs = rhs
    
    def get_params(self):
        result = []
        result.extend(self._lhs.get_params())
        result.extend(self._rhs.get_params())
        return tuple(result)

class _ChainableOperator(_OperatorExpr):
    """SQL chainable operator.
    
    This can be used to implement operators that are both
    associative and commutative.
    See `Or_`, `And_`, or `Plus_` as an example."""
    def __init__(self, *operands):
        self._operands = operands
    
    def get_params(self):
        result = []
        for operand in self._operands:
            result.extend(operand.get_params())
        return result

class Or_(_ChainableOperator):
    """SQL 'OR' operator"""
    def ref_field(self):
        return ' OR '.join(
            ['({})'.format(expr.ref_field()) for expr in self._operands])

class And_(_ChainableOperator):
    """SQL 'AND' operator"""
    def ref_field(self):
        return ' AND '.join(
            ['({})'.format(expr.ref_field()) for expr in self._operands])

class Not_(_UnaryOperator):
    """SQL 'NOT' operator"""
    def ref_field(self):
        return 'NOT ({})'.format(self._operand.ref_field())

class Is_(_BinaryOperator):
    """SQL 'IS' operator"""
    def ref_field(self):
        return '({}) IS ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class IsNull_(_UnaryOperator):
    """SQL 'IS NULL' operator"""
    def ref_field(self):
        return '({} IS NULL)'.format(self._operand.ref_field())

class NotNull_(_UnaryOperator):
    """SQL 'IS NOT NULL' operator"""
    def ref_field(self):
        return '({}) IS NOT NULL'.format(self._operand.ref_field())

class Equal_(_BinaryOperator):
    """SQL '=' operator"""
    def ref_field(self):
        return '({}) = ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class NotEqual_(_BinaryOperator):
    """SQL '!=' or '<>' operator"""
    def ref_field(self):
        return '({}) <> ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class LessThan_(_BinaryOperator):
    """SQL '<' operator"""
    def ref_field(self):
        return '({}) < ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class GreaterThan_(_BinaryOperator):
    """SQL '>' operator"""
    def ref_field(self):
        return '({}) > ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class LessThanEqual_(_BinaryOperator):
    """SQL '<=' operator"""
    def ref_field(self):
        return '({}) <= ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class GreaterThanEqual_(_BinaryOperator):
    """SQL '>=' operator"""
    def ref_field(self):
        return '({}) >= ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

# BETWEEN IN LIKE ILIKE SIMILAR

# (any other operator)

class Plus_(_ChainableOperator):
    """SQL '+' operator"""
    def ref_field(self):
        return ' + '.join(
            ['({})'.format(expr.ref_field()) for expr in self._operands])

class Minus_(_BinaryOperator):
    """SQL '-' operator"""
    def ref_field(self):
        return '({}) - ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class Mult_(_ChainableOperator):
    """SQL '*' operator"""
    def ref_field(self):
        return ' * '.join(
            ['({})'.format(expr.ref_field()) for expr in self._operands])

class Div_(_BinaryOperator):
    """SQL '/' operator"""
    def ref_field(self):
        return '({}) / ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class Mod_(_BinaryOperator):
    """SQL '%' operator"""
    def ref_field(self):
        return '({}) % ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class Exp_(_BinaryOperator):
    """SQL '^' operator"""
    def ref_field(self):
        return '({}) ^ ({})'.format(
			self._lhs.ref_field(), self._rhs.ref_field())

class UnaryPlus_(_UnaryOperator):
    """SQL Unary '+' operator"""
    def ref_field(self):
        return '+({})'.format(self._operand.ref_field())

class UnaryMinus_(_UnaryOperator):
    """SQL Unary '-' operator"""
    def ref_field(self):
        return '-({})'.format(self._operand.ref_field())

Queryable.register(_OperatorExpr)
Queryable.register(_AliasedOperatorExpr)
