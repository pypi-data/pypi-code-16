import copy

from sqc.src.Operand import Operand

from sqc.src.operations import BinOp, UnOp, VectorUnOp, VectorBinOp
from sqc.src.operations import oper_actions


class Node:
    """
    Node class.
        value:      NodeValue object
        children:   list of outgoing nodes
    """

    def __init__(self, value):
        self.value = value
        self.children = []
        self.parent = None

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
        value_children = \
            [child for child in self.children if child.value.is_operand() and child.value.operand.is_numeric_value()]
        if self.value.is_operation() and isinstance(self.value.operation, BinOp) and \
           len(value_children) == 2:
            values = [child.value.operand.numeric_value for child in self.children]
            value = oper_actions[self.value.operation](values[0], values[1])

            self.children = []
            self.value = NodeValue(operand=Operand(numeric_value=value))

        elif self.value.is_operation() and isinstance(self.value.operation, UnOp) and len(value_children) == 1:
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

        elif self.value.is_operation() and (isinstance(self.value.operation, VectorBinOp)):
            is_mult_by_num = False
            is_get_ind = False
            args_are_numeric_values = True
            if self.value.operation == VectorBinOp.MultByNum:
                is_mult_by_num = True
                if not self.children[0].value.operand.is_numeric_value():
                    self.children[0], self.children[1] = self.children[1], self.children[0]
                if not self.children[0].value.operand.is_numeric_value():
                    raise ValueError('Wrong multiplication parameter')
            if self.value.operation == VectorBinOp.GetInd:
                is_get_ind = True
                if not self.children[1].value.operand.is_numeric_value():
                    raise ValueError('Wrong get index parameter')

            for i in range(int(is_mult_by_num), 2 - int(is_get_ind)):
                if self.children[i].value.is_operand():
                    if self.children[i].value.operand.is_vector():
                        for node in self.children[i].value.operand.vector_elements:
                            if node.value.operand.is_vector():
                                for node2 in node.value.operand.vector_elements:
                                    if not node2.value.operand.is_numeric_value():
                                        args_are_numeric_values = False
                                        break
                                if not args_are_numeric_values:
                                    break
                            else:
                                if not node.value.operand.is_numeric_value():
                                    args_are_numeric_values = False
                                    break
                    elif not self.children[i].value.operand.is_variable():
                        raise ValueError('Binary vector operation arguments error')
                    else:
                        args_are_numeric_values = False
                        break
                else:
                    args_are_numeric_values = False
                    break

            if args_are_numeric_values:
                self.value = oper_actions[self.value.operation](
                    self.children[0].value.operand,
                    self.children[1].value.operand
                ).value
                self.children = []

        elif self.value.is_operation() and (isinstance(self.value.operation, VectorUnOp)):
            args_are_numeric_values = True
            if self.children[0].value.is_operand():
                if self.children[0].value.operand.is_vector():
                    for node in self.children[0].value.operand.vector_elements:
                        if node.value.operand.is_vector():
                            for node2 in node.value.operand.vector_elements:
                                if not node2.value.operand.is_numeric_value():
                                    args_are_numeric_values = False
                                    break
                            if not args_are_numeric_values:
                                break
                        else:
                            if not node.value.operand.is_numeric_value():
                                args_are_numeric_values = False
                                break
                elif not self.children[0].value.operand.is_variable():
                    raise ValueError('Binary vector operation arguments error')
                else:
                    args_are_numeric_values = False
            else:
                args_are_numeric_values = False

            if args_are_numeric_values:
                self.value = oper_actions[self.value.operation](self.children[0].value.operand).value
                self.children = []

    def unify(self, rule_node):
        if self.value is None:
            return None

        if self.value.is_operand() and not rule_node.value.is_operand():
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
            elif not self.value.operand.is_vector():
                result_data[rule_node.value.operand.variable] = copy.copy(self)
            else:
                return None

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


class NodeValue:
    """
    NodeValue can be whether an operation or operand.
    """

    def __init__(self, operation=None, operand=None):
        """

        :param operation:
        :type operation:
        :param operand:
        :type operand:
        """

        if operation is not None:
            self.type = 0
            self.operation = operation
        else:
            self.type = 1
            self.operand = operand

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
            return NodeValue(operation=self.operation)
        else:
            return NodeValue(operand=copy.copy(self.operand))

    def is_operation(self):
        return self.type == 0

    def is_operand(self):
        return self.type == 1
