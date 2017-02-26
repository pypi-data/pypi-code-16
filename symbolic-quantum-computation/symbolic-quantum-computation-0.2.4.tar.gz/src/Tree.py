import ast
import copy
from src.Operand import Operand
from src.operations import ast_bin_ops, ast_un_ops
from src.operations import BinOp, UnOp
from src.operations import oper_symbols, oper_actions
from src.misc import get_index
from src.Node import Node, NodeValue


class Tree:
    """
    Abstract syntax tree class.
    """

    def __init__(self, ast_tree=None, expression=None, root=None):
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

                df_walk(ast_node.left, new_node)
                df_walk(ast_node.right, new_node)
            elif isinstance(ast_node, ast.UnaryOp):
                new_node = Node(NodeValue(operation=ast_un_ops[type(ast_node.op).__name__]))
                custom_parent_node.add_child(new_node)

                df_walk(ast_node.operand, new_node)
            elif isinstance(ast_node, ast.Name):
                new_node = Node(NodeValue(operand=Operand(1, variable=ast_node.id)))
                custom_parent_node.add_child(new_node)
            elif isinstance(ast_node, ast.Num):
                new_node = Node(NodeValue(operand=Operand(1, numeric_value=ast_node.n)))
                custom_parent_node.add_child(new_node)

        if root is not None:
            self.root = root
        else:
            # Create fictitious root node
            self.root = Node(None)

            if ast_tree is None:
                ast_tree = ast.parse(expression)
            df_walk(ast_tree, self.root)

            # Remove fictitious root node
            if len(self.root.children) > 0:
                self.root = self.root.children[0]
            self.root.parent = None

        self.current_node = self.root

    def __str__(self):
        def dfs(node, depth):
            result = ''
            if node.value.is_operation():
                result += '\t' * depth + str(node.value) + '\n'
                for child in node.children:
                    result += dfs(child, depth + 1)
            else:
                result = '\t' * depth + str(node.value) + '\n'

            return result

        output = ''
        if self.root.value is not None:
            output = dfs(self.root, 0)

        return output

    def __eq__(self, other):
        return self.root.eq_subtrees(other.root)

    def node_list(self):
        def dfs(node):
            nodes = [node]
            for child in node.children:
                nodes.extend(dfs(child))
            return nodes

        return dfs(self.root)

    def tree_calculate(self):
        def dfs(node):
            for child in node.children:
                dfs(child)
            node.calculate()

        if self.root.value is not None:
            dfs(self.root)

    def to_expression(self):
        """
        Transform tree to expression.
        :return:    Expression string.
        :rtype:     string
        """

        def dfs(node):
            if node.value.is_operation():
                if isinstance(node.value.operation, UnOp):
                    result = oper_symbols[node.value.operation]
                else:
                    result = ''

                for i in range(len(node.children)):
                    child = node.children[i]
                    if child.value.is_operation() and \
                       (
                               (
                                       node.value.operation == BinOp.Mult and
                                       (child.value.operation == BinOp.Add or child.value.operation == BinOp.Sub)
                               ) or
                               (node.value.operation == BinOp.Sub and i == 1) or
                               (node.value.operation == BinOp.Div and i == 1) or
                               node.value.operation == BinOp.Pow or
                               isinstance(node.value.operation, UnOp) or
                               isinstance(child.value.operation, UnOp)
                       ):
                        result += '(' + dfs(child) + ')'
                    else:
                        result += dfs(child)

                    if i != len(node.children) - 1:
                        result += oper_symbols[node.value.operation]
            else:
                if node.value.operand.is_numeric_value() and node.value.operand.numeric_value < 0 and\
                   node.parent is not None:
                    result = '(' + str(node.value) + ')'
                else:
                    result = str(node.value)

            return result

        output = ''
        if self.root.value is not None:
            output = dfs(self.root)

        return output

    def next_node(self):
        if len(self.current_node.children) == 0:
            parent = self.current_node.parent
            while parent is not None and\
                    get_index(parent.children, self.current_node) == len(parent.children) - 1:
                self.current_node = parent
                parent = parent.parent

            if parent is None:
                self.current_node = self.root
                return None
            else:
                self.current_node = parent.children[parent.children.index(self.current_node) + 1]
        else:
            self.current_node = self.current_node.children[0]

        return self.current_node

    def get_copy(self):
        """
        Return copy of the tree.
        :return:
        :rtype:     Tree
        """
        def dfs(orig_node, copy_parent):
            new_node = Node(copy.copy(orig_node.value))
            copy_parent.add_child(new_node)
            for child in orig_node.children:
                dfs(child, new_node)

        tmp_root = Node(None)
        dfs(self.root, tmp_root)
        if len(tmp_root.children) > 0:
            tmp_root = tmp_root.children[0]

        return Tree(root=tmp_root)


class Rules:
    def __init__(self):
        self.data = []
        with open('rules.txt', 'r') as f:
            rules = f.read().split("\n")
            for rule in rules:
                left, right = rule.split('=')
                self.data.append((Tree(expression=left), Tree(expression=right)))

    def __iter__(self):
        for it in self.data:
            yield it
