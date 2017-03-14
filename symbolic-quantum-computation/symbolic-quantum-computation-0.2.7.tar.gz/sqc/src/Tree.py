import ast
import copy
import os

from sqc.src.Node import Node, NodeValue
from sqc.src.Operand import Operand
from sqc.src.misc import get_index

from sqc.src.operations import BinOp, UnOp, functions
from sqc.src.operations import ast_bin_ops, ast_un_ops
from sqc.src.operations import oper_symbols


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

        def df_walk(ast_node):
            """
            Depth-first walk on the tree.

            :param ast_node:            Built-in ast node.
            :type ast_node:             ast.Module, ast.Expr, ast.BinOp, UnaryOp, ast.Name, ast.Num, ast.Call, ast.List
            :return:
            :rtype:                     Node
            """

            new_node = None
            if isinstance(ast_node, ast.Module):
                if len(ast_node.body) > 0:
                    new_node = df_walk(ast_node.body[0])

            elif isinstance(ast_node, ast.Expr):
                new_node = df_walk(ast_node.value)

            elif isinstance(ast_node, ast.BinOp):
                new_node = Node(NodeValue(operation=ast_bin_ops[type(ast_node.op).__name__]))
                
                new_node.add_child(df_walk(ast_node.left))
                new_node.add_child(df_walk(ast_node.right))

            elif isinstance(ast_node, ast.UnaryOp):
                new_node = Node(NodeValue(operation=ast_un_ops[type(ast_node.op).__name__]))

                new_node.add_child(df_walk(ast_node.operand))

            elif isinstance(ast_node, ast.Name):
                new_node = Node(NodeValue(operand=Operand(variable=ast_node.id)))

            elif isinstance(ast_node, ast.Num):
                new_node = Node(NodeValue(operand=Operand(numeric_value=ast_node.n)))

            elif isinstance(ast_node, ast.Call):
                if len(ast_node.args) == 2:
                    new_node = Node(NodeValue(operation=ast_bin_ops[ast_node.func.id]))

                    new_node.add_child(df_walk(ast_node.args[0]))
                    new_node.add_child(df_walk(ast_node.args[1]))
                elif len(ast_node.args) == 1:
                    new_node = Node(NodeValue(operation=ast_un_ops[ast_node.func.id]))
                    new_node.add_child(df_walk(ast_node.args[0]))
            elif isinstance(ast_node, ast.List):
                vector_elements = []
                if len(ast_node.elts) == 0:
                    raise ValueError('Empty vector error')
                for node in ast_node.elts:
                    vector_elements.append(df_walk(node))
                new_node = Node(NodeValue(operand=Operand(vector_elements=vector_elements)))
                
            return new_node
        if root is not None:
            self.root = root
        else:
            if ast_tree is None:
                ast_tree = ast.parse(expression)
            self.root = df_walk(ast_tree)
            if self.root is None:
                self.root = Node(None)

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
                if node.value.operation in functions:
                    result = oper_symbols[node.value.operation] + '('

                for i in range(len(node.children)):
                    child = node.children[i]
                    if child.value.is_operation() and child.value.operation not in functions:
                        result += '(' + dfs(child) + ')'
                        if node.value.is_operation() and node.value.operation in functions:
                            if i != len(node.children) - 1:
                                result += ', '
                    else:
                        result += dfs(child)
                        if node.value.operation in functions:
                            if i != len(node.children) - 1:
                                result += ', '

                    if i != len(node.children) - 1 and node.value.operation not in functions:
                        result += oper_symbols[node.value.operation]

                if node.value.operation in functions:
                    result += ')'
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
        with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/rules.txt', 'r') as f:
            rules_lines = f.read().split("\n")
            for line in rules_lines:
                self.data.append(self.get_rule_from_string(line))

    def __iter__(self):
        for it in self.data:
            yield it

    @staticmethod
    def get_rule_from_string(string):
        left, right = string.split('=')
        return Tree(expression=left), Tree(expression=right)

    @staticmethod
    def apply_rule(node, rule):
        unify_result = node.unify(rule[0].root)
        if unify_result is not None:
            node.replace(rule)

    def get_possible_rules(self, node, tree):
        result = []
        node_copy = copy.copy(node)

        for rule in self.data:
            if node.unify(rule[0].root) is not None:
                node.replace(rule)

                copy_tree = tree.get_copy()
                result.append((copy_tree, rule))

                node.value = node_copy.value
                node.children = node_copy.children

        for child in node.children:
            result.extend(self.get_possible_rules(child, tree))

        return result
