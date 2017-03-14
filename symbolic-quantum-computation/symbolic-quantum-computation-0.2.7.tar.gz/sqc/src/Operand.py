import copy
from sqc.src.Constant import constants


class Operand:
    """
    Operand can be whether a numeric value or variable of given dimension.
    """
    def __init__(self, numeric_value=None, variable=None, vector_elements=None):
        """
        :param numeric_value:   Number/vector/matrix
        :type numeric_value:    int, float
        :param variable:        Name of the variable or list/matrix of variable.
        :type variable:         string
        :param vector_elements: List of nodes
        :type vector_elements:  list
        """

        self._is_constant = False
        self.shape = None
        if numeric_value is not None:
            self.shape = ()
            self.type = 0
            self.numeric_value = numeric_value
        elif variable is not None:
            self.type = 1
            self.variable = variable
            if self.variable in constants.keys():
                self._is_constant = True
        else:
            self.type = 2
            self.vector_elements = vector_elements

            elem_shape = None
            for node in self.vector_elements:
                if node.value.is_operand():
                    if node.value.operand.is_variable() and not node.value.operand.is_constant():
                        elem_shape = None
                        break
                    elif node.value.operand.is_numeric_value() or node.value.operand.is_constant():
                        if elem_shape is None:
                            elem_shape = ()
                        elif elem_shape != ():
                            raise ValueError('Vector elements shape error')
                    elif node.value.operand.is_vector():
                        if elem_shape is None:
                            elem_shape = (len(node.value.operand.vector_elements), )
                        elif elem_shape != (len(node.value.operand.vector_elements), ):
                            raise ValueError('Vector elements shape error')
                else:
                    raise ValueError('Operation in vector element is not allowed yet')

            if elem_shape is not None:
                if elem_shape == ():
                    self.shape = (1, len(self.vector_elements))
                else:
                    self.shape = (len(self.vector_elements), elem_shape[0])

    def __str__(self):
        if self.is_numeric_value():
            return str(self.numeric_value)
        elif self.is_variable():
            return str(self.variable)
        else:
            result = '['
            for it in self.vector_elements:
                result += str(it) + ', '
            if len(result) > 1:
                return result[0:-2] + ']'
            else:
                return '[]'

    def __eq__(self, other):
        if self.is_variable():
            return other.is_variable() and self.variable == other.variable
        elif self.is_numeric_value():
            return other.is_numeric_value() and self.numeric_value == other.numeric_value
        else:
            if other.is_vector() and len(other.vector_elements) == len(self.vector_elements):
                eq = True
                for i in range(len(self.vector_elements)):
                    eq = self.vector_elements[i].eq_subtrees(other.vector_elements[i])
                    if not eq:
                        break
                return eq
            else:
                return False

    def __copy__(self):
        if self.is_numeric_value():
            return Operand(numeric_value=self.numeric_value)
        elif self.is_variable():
            return Operand(variable=self.variable)
        else:
            vector_elements = []
            for it in self.vector_elements:
                vector_elements.append(copy.copy(it))
            return Operand(vector_elements=vector_elements)

    def is_numeric_value(self):
        return self.type == 0

    def is_variable(self):
        return self.type == 1

    def is_vector(self):
        return self.type == 2

    def is_constant(self):
        return self._is_constant
