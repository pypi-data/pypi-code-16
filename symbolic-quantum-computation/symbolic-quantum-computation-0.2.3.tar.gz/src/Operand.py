class Operand:
    """
    Operand can be whether a numeric value or variable of given dimension.
    """
    def __init__(self, dim, numeric_value=None, variable=None):
        """
        :param dim:             Dimension of value/variable.
        :type dim:              int
        :param numeric_value:   Number/vector/matrix
        :type numeric_value:    int, float, list
        :param variable:        Name of the variable or list/matrix of variable.
        :type variable:         string, list
        """
        if not (numeric_value is not None and variable is None or
                numeric_value is None and variable is not None):
            raise ValueError('Wrong Operand init parameters')

        self.dim = dim
        if numeric_value is not None:
            self.type = 0
            self.numeric_value = numeric_value
        else:
            self.type = 1
            self.variable = variable

    def is_numeric_value(self):
        return self.type == 0

    def is_variable(self):
        return self.type == 1

    def __str__(self):
        if self.is_numeric_value():
            return str(self.numeric_value)
        else:
            return str(self.variable)

    def __eq__(self, other):
        return self.is_variable() and other.is_variable() and self.variable == other.variable or\
           self.is_numeric_value() and other.is_numeric_value() and self.numeric_value == other.numeric_value
