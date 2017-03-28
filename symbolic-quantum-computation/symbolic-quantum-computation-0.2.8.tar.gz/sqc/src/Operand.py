import copy
from sqc.src.Constant import constants


class Operand:
    """
    Operand can be whether a numeric value or variable of given dimension.
    """
    def __init__(self, numeric_value=None, variable=None, shape=None):
        """
        :param numeric_value:   Number/vector/matrix
        :type numeric_value:    int, float
        :param variable:        Name of the variable or list/matrix of variable.
        :type variable:         string
        """

        self._is_constant = False
        self.shape = shape
        if numeric_value is not None:
            self.shape = ()
            self.type = 0
            self.numeric_value = numeric_value
        elif variable is not None:
            self.type = 1
            self.variable = variable
            if self.variable in constants.keys():
                self.shape = ()
                self._is_constant = True

    def __str__(self):
        if self.is_numeric_value():
            return str(self.numeric_value)
        elif self.is_variable():
            return str(self.variable)
        else:
            return '[]'

    def __eq__(self, other):
        if self.is_variable():
            return other.is_variable() and self.variable == other.variable
        elif self.is_numeric_value():
            return other.is_numeric_value() and self.numeric_value == other.numeric_value

    def __copy__(self):
        if self.is_numeric_value():
            return Operand(numeric_value=self.numeric_value)
        elif self.is_variable():
            return Operand(variable=self.variable, shape=self.shape)

    def is_numeric_value(self):
        return self.type == 0

    def is_variable(self):
        return self.type == 1

    def is_constant(self):
        return self._is_constant
