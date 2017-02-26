import copy
from src.Operand import Operand
from src.operations import BinOp
from src.operations import oper_actions


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
            self.value = NodeValue(operand=Operand(dim=1, numeric_value=value))

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
                if rule_node.value.operand.is_numeric_value():
                    return None
                else:
                    result_data[rule_node.value.operand.variable] = copy.copy(self)
        else:
            if rule_node.value.operand.is_numeric_value():
                if self.value != rule_node.value:
                    return None
            else:
                result_data[rule_node.value.operand.variable] = copy.copy(self)

        return result_data

    def replace(self, rule):
        substitutions = self.unify(rule[0].root)

        def dfs(rule_node, parent, substitutions):
            if rule_node.value.is_operand():
                if rule_node.value.operand.is_variable():
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
        if not (operation is not None and operand is None or
           operation is None and operand is not None):
            raise ValueError('Wrong Node init parameters')

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
        return self.is_operation() and other.is_operation() and self.operation == other.operation or \
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
