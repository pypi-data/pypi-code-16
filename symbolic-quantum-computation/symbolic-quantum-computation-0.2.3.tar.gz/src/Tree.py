import ast
from src.Operand import Operand
from src.operations import ast_bin_ops, ast_un_ops


class Tree:
    """
    Abstract syntax tree class.
    """
    def __init__(self, ast_tree=None, expression=None):
        """
            Copies ast.

            :param ast_tree:    Built-in abstract syntax tree.
            :type ast_tree:     ast.Module
            :param expression:  Arithmetic expression
            :type expression:   string
            :return:            Rebuilt abstract syntax tree.
            :rtype:             Tree
            """

        def df_walk(ast_node, custom_parent_node):
            """
            Depth-first walk on the tree.

            :param ast_node:            Built-in ast node.
            :type ast_node:             ast.Module, ast.Expr, ast.BinOp, UnaryOp, ast.Name, ast.Num
            :param custom_parent_node:  Custom tree parent node.
            :type custom_parent_node:   Node
            :return:
            :rtype:                     None
            """

            if isinstance(ast_node, ast.Module):
                if len(ast_node.body) > 0:
                    df_walk(ast_node.body[0], custom_parent_node)
            elif isinstance(ast_node, ast.Expr):
                df_walk(ast_node.value, custom_parent_node)
            elif isinstance(ast_node, ast.BinOp):
                new_node = Node(NodeValue(operation=ast_bin_ops[type(ast_node.op).__name__]))
                custom_parent_node.add_child(new_node)
                new_node.parent = custom_parent_node

                df_walk(ast_node.left, new_node)
                df_walk(ast_node.right, new_node)
            elif isinstance(ast_node, ast.UnaryOp):
                new_node = Node(NodeValue(operation=ast_un_ops[type(ast_node.op).__name__]))
                custom_parent_node.add_child(new_node)
                new_node.parent = custom_parent_node

                df_walk(ast_node.operand, new_node)
            elif isinstance(ast_node, ast.Name):
                new_node = Node(NodeValue(operand=Operand(1, variable=ast_node.id)))
                custom_parent_node.add_child(new_node)
                new_node.parent = custom_parent_node
            elif isinstance(ast_node, ast.Num):
                new_node = Node(NodeValue(operand=Operand(1, numeric_value=ast_node.n)))
                custom_parent_node.add_child(new_node)
                new_node.parent = custom_parent_node

        # Create fictitious root node
        self.root = Node(None)

        if ast_tree is None:
            ast_tree = ast.parse(expression)
        df_walk(ast_tree, self.root)

        # Remove fictitious root node
        if len(self.root.children) > 0:
            self.root = self.root.children[0]
        
    def __str__(self):
        def dfs(node, depth):
            result = ''
            if node.value.is_operation():
                result += '\t'*depth + str(node.value) + '\n'
                for child in node.children:
                    result += dfs(child, depth + 1)
            else:
                result = '\t'*depth + str(node.value) + '\n'

            return result

        output = ''
        if self.root.value is not None:
            output = dfs(self.root, 0)

        return output

    def __eq__(self, other):
        return self.root.eq_subtrees(other.root)

    @staticmethod
    def iter_child_nodes(node):
        for child in node.children:
            yield child


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

    def __eq__(self, other):
        return self.value == other.value and len(self.children) == len(other.children)

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
            return str(self.operand)
        else:
            return str(self.operation.name)

    def __eq__(self, other):
        return self.is_operation() and other.is_operation() and self.operation == other.operation or\
           self.is_operand() and other.is_operand() and self.operand == other.operand
