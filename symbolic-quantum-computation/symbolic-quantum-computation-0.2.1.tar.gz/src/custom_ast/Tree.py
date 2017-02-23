

class Tree:
    """
    Abstract syntax tree class.
    """
    def __init__(self, root):
        self.root = root
        
    def __str__(self):
        def dfs(node, depth):
            result = ''
            if node.value.is_operation():
                result += '\t' * depth + node.value.operation.name + '\n'
                for child in node.children:
                    result += dfs(child, depth + 1)
            else:
                result = '\t'*depth + str(node.value.operand) + '\n'

            return result

        output = ''
        if self.root.value is not None:
            output = dfs(self.root, 0)

        return output

    def __eq__(self, other):
        pass


class Node:
    """
    Node class.
        value:      NodeValue object
        children:   list of outgoing nodes
    """
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)


class NodeValue:
    """
    NodeValue can be whether an operation or operand.
    """
    def __init__(self, operation=None, operand=None):
        if not(operation is not None and operand is None or
               operation is None and operand is not None):
            raise ValueError('Wrong Node init parameters')

        if operation is not None:
            self.type = 0
            self.operation = operation
        else:
            self.type = 1
            self.operand = operand

    def is_operation(self):
        return self.type == 0

    def is_operand(self):
        return self.type == 1

    def __str__(self):
        if self.is_operand():
            print(self.operand)
        else:
            print(self.operation)

    def __eq__(self, other):
        if self.is_operation() and other.is_operation() and self.operation == other.operation or\
           self.is_operand() and other.is_operand() and self.operand == other.operand:
            return True