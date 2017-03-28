import copy

from sqc.src.Operand import Operand

from sqc.src.operations import BinOp, UnOp, VectorUnOp, VectorBinOp, VectorOp
from sqc.src.operations import oper_actions


class Node:
    """
    Node class.
        value:      NodeValue object
        children:   list of outgoing nodes
    """

    def __init__(self, value, subroot=False):
        self.value = value
        self.children = []
        self.parent = None
        self.subroot = subroot

    def __eq__(self, other):
        return self.value == other.value and len(self.children) == len(other.children)

    def __str__(self):
        return str(self.value)

    def __copy__(self):
        result = Node(copy.copy(self.value))
        for child in self.children:
            result.add_child(copy.copy(child))
        return result

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def eq_subtrees(self, other):
        """
        Recursive function for checking whether subtrees are equal.

        :param other:   another node
        :type other:    Node
        :return:        True if corresponding subtrees are equal, False o/w.
        :rtype:         bool
        """

        result = self == other
        if result:
            for i in range(len(self.children)):
                child = self.children[i]
                other_child = other.children[i]

                result &= child.eq_subtrees(other_child)
                if not result:
                    break
        return result

    def calculate(self):
        """
        Tries to calculate children. (for binary trees only)
        :return:
        :rtype:
        """
        def all_children_are_numeric_values(node):
            result = True
            if node.value.is_operand() and not node.value.operand.is_numeric_value():
                result = False

            if result:
                for child_node in node.children:
                    result &= all_children_are_numeric_values(child_node)

                    if not result:
                        break

            return result

        if self.value.is_operation():
            if isinstance(self.value.operation, BinOp) and all_children_are_numeric_values(self):
                values = [child.value.operand.numeric_value for child in self.children]
                value = oper_actions[self.value.operation](values[0], values[1])

                self.children = []
                self.value = NodeValue(operand=Operand(numeric_value=value))
                self.value.shape = ()
                if isinstance(self.value.operand.numeric_value, complex):
                    complex_number = self.value.operand.numeric_value

                    self.value = NodeValue(operation=BinOp.Add)

                    self.add_child(Node(NodeValue(operand=Operand(numeric_value=complex_number.real))))
                    self.children[0].value.shape = ()

                    self.add_child(Node(NodeValue(operation=BinOp.Mult)))
                    self.children[1].value.shape = ()

                    self.children[1].add_child(Node(NodeValue(operand=Operand(numeric_value=complex_number.imag))))
                    self.children[1].children[0].value.shape = ()

                    self.children[1].add_child(Node(NodeValue(operand=Operand(variable='i'))))
                    self.children[1].children[1].value.shape = ()

            elif isinstance(self.value.operation, UnOp) and all_children_are_numeric_values(self):
                values = [child.value.operand.numeric_value for child in self.children]
                if self.value.operation == UnOp.UAdd:
                    self.children = []
                    self.value = NodeValue(operand=Operand(numeric_value=values[0]))
                elif self.value.operation == UnOp.USub:
                    self.children = []
                    self.value = NodeValue(operand=Operand(numeric_value=-values[0]))
                else:
                    value = oper_actions[self.value.operation](values[0])

                    self.children = []
                    self.value = NodeValue(operand=Operand(numeric_value=value))
                self.value.shape = ()

            elif isinstance(self.value.operation, VectorBinOp):
                if all_children_are_numeric_values(self):
                    new_node = oper_actions[self.value.operation](self.children[0], self.children[1])
                    new_node.value.shape = self.value.shape
                    self.value = new_node.value
                    self.children = new_node.children

            elif isinstance(self.value.operation, VectorUnOp):
                if all_children_are_numeric_values(self):
                    new_node = oper_actions[self.value.operation](self.children[0])
                    new_node.value.shape = self.value.shape
                    self.value = new_node.value
                    self.children = new_node.children

    def unify(self, rule_node):
        if self.value is None:
            return None

        if self.value.is_operand() and not rule_node.value.is_operand() or\
           (self.value.is_operation() and self.value.operation == VectorOp):
            return None

        result_data = {}
        if self.value.is_operation():
            if rule_node.value.is_operation():
                if len(self.children) != len(rule_node.children) or\
                   self.value.operation != rule_node.value.operation:
                    return None
                for i in range(len(self.children)):
                    inter_result = self.children[i].unify(rule_node.children[i])

                    if inter_result is None:
                        return None

                    for key, value in inter_result.items():
                        if key in result_data:
                            if not value.eq_subtrees(result_data[key]):
                                return None
                        else:
                            result_data[key] = value
            else:
                if not rule_node.value.operand.is_variable() or rule_node.value.operand.is_constant():
                    return None
                else:
                    result_data[rule_node.value.operand.variable] = copy.copy(self)
        else:
            if rule_node.value.operand.is_numeric_value() or rule_node.value.operand.is_constant():
                if self.value != rule_node.value:
                    return None
            else:
                result_data[rule_node.value.operand.variable] = copy.copy(self)

        return result_data

    def replace(self, rule):
        substitutions = self.unify(rule[0].root)

        def dfs(rule_node, parent, substitutions):
            if rule_node.value.is_operand():
                if rule_node.value.operand.is_variable() and not rule_node.value.operand.is_constant():
                    new_node = copy.copy(substitutions[rule_node.value.operand.variable])
                else:
                    new_node = copy.copy(rule_node)
                parent.add_child(new_node)
            else:
                new_node = Node(copy.copy(rule_node.value))
                parent.add_child(new_node)

                for i in range(len(rule_node.children)):
                    dfs(rule_node.children[i], new_node, substitutions)

        tmp_root = Node(value=None)
        dfs(rule[1].root, tmp_root, substitutions)

        new_root = tmp_root.children[0]
        self.value = new_root.value
        self.children = new_root.children

    def set_shape(self):
        # for child_node in self.children:
        #     child_node.set_shapes()

        for child_node in self.children:
            if child_node.value.shape is None:
                raise ValueError('Set shape error. Children shape is not defined')

        if self.value.is_operand():
            if self.value.operand.shape is None:
                raise ValueError('Operand without shape')
            self.value.shape = self.value.operand.shape
        else:
            if isinstance(self.value.operation, BinOp):
                if not self.children[0].value.shape == self.children[1].value.shape == ():
                    raise ValueError('Wrong shapes for number binary operation.')
                self.value.shape = self.children[0].value.shape

            elif isinstance(self.value.operation, UnOp):
                if self.children[0].value.shape != ():
                    raise ValueError('Wrong shapes for number unary operation.')
                self.value.shape = self.children[0].value.shape

            elif isinstance(self.value.operation, VectorBinOp):
                if self.value.operation == VectorBinOp.Add or self.value.operation == VectorBinOp.Sub:
                    if self.children[0].value.shape != self.children[1].value.shape or\
                       self.children[0].value.shape == ():
                        raise ValueError('Wrong vector addition/subtraction arguments')
                    self.value.shape = self.children[0].value.shape

                elif self.value.operation == VectorBinOp.MultByNum:
                    if not (self.children[0].value.shape != () and self.children[1].value.shape == () or
                            self.children[0].value.shape == () and self.children[1].value.shape != ()):
                        raise ValueError('Wrong vector multiplication by number error')

                    if self.children[0].value.shape == ():
                        self.value.shape = self.children[1].value.shape
                    else:
                        self.value.shape = self.children[0].value.shape

                elif self.value.operation == VectorBinOp.DotProd:
                    if not (self.children[0].value.shape[0] == self.children[1].value.shape[0] == 1):
                        raise ValueError('Wrong vector dot product arguments')

                    self.value.shape = ()

                elif self.value.operation == VectorBinOp.GetInd:
                    if not (self.children[0].value.shape != () and self.children[1].value.shape == ()):
                        raise ValueError('Wrong vector multiplication by number error')

                    if self.children[0].value.shape[0] == 1:
                        self.value.shape = self.children[0].children[0].children[0].value.shape
                    else:
                        self.value.shape = self.children[0].children[0].value.shape

                elif self.value.operation == VectorBinOp.Mult:
                    if self.children[0].value.shape[1] != self.children[1].value.shape[0] or\
                       self.children[0].value.shape == ():
                        raise ValueError('Wrong vector multiplication arguments')
                    self.value.shape = (self.children[0].value.shape[0], self.children[1].value.shape[1])

                elif self.value.operation == VectorBinOp.TensMult:
                    if self.children[0].value.shape == () or self.children[1].value.shape == ():
                        raise ValueError('Wrong tensor multiplication arguments')
                    self.value.shape = (self.children[0].value.shape[0]*self.children[1].value.shape[0],
                                        self.children[0].value.shape[1]*self.children[1].value.shape[1])

            elif isinstance(self.value.operation, VectorUnOp):
                if self.children[0].value.shape == ():
                    raise ValueError('Wrong vector unary minus argument')
                if self.value.operation == VectorUnOp.USub:
                    self.value.shape = self.children[0].value.shape

                elif self.value.operation == VectorUnOp.Transpose:
                    if self.children[0].value.shape == ():
                        raise ValueError('Wrong vector transpose argument')
                    self.value.shape = (self.children[0].value.shape[1], self.children[0].value.shape[0])

            elif isinstance(self.value.operation, VectorOp):
                elem_shapes = set()
                for child_node in self.children:
                    elem_shapes.add(child_node.value.shape)
                if None in elem_shapes:
                    raise ValueError('Vector element shape is not set')
                if len(elem_shapes) == 0:
                    raise ValueError('Empty vector')
                if len(elem_shapes) > 1:
                    raise ValueError('Vector element shapes are different')

                elem_shape = list(elem_shapes)[0]
                if not(len(elem_shape) == 0 or len(elem_shape) == 2):
                    raise ValueError('Wrong subvector shapes')
                if elem_shape == ():
                    self.value.shape = (1, len(self.children))
                else:
                    self.value.shape = (len(self.children), elem_shape[1])


class NodeValue:
    """
    NodeValue can be whether an operation or operand.
    """

    def __init__(self, operation=None, operand=None, shape=None):
        """

        :param operation:
        :type operation:
        :param operand:
        :type operand:
        """

        self.shape = shape
        if operation is not None:
            self.type = 0
            self.operation = operation
        else:
            self.type = 1
            self.operand = operand
            if self.shape is None:
                self.shape = self.operand.shape

    def __str__(self):
        if self.is_operand():
            return str(self.operand)
        else:
            return str(self.operation.name)

    def __eq__(self, other):
        return self.is_operation() and other.is_operation() and self.operation == other.operation or\
                self.is_operand() and other.is_operand() and self.operand == other.operand

    def __copy__(self):
        if self.is_operation():
            return NodeValue(operation=self.operation, shape=self.shape)
        else:
            return NodeValue(operand=copy.copy(self.operand), shape=self.shape)

    def is_operation(self):
        return self.type == 0

    def is_operand(self):
        return self.type == 1
