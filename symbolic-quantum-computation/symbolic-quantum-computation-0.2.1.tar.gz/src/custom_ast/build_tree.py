import ast
from src.custom_ast.Tree import Tree, Node, NodeValue
from src.opers import BinOp, UnOp, Operand


# ast available binary operations
ast_bin_ops = {
    'Add': BinOp.Add,
    'Sub': BinOp.Sub,
    'Mult': BinOp.Mult,
    'Div': BinOp.Div,
    'Pow': BinOp.Pow
}

# ast available unary operations
ast_un_ops = {
    'UAdd': UnOp.UAdd,
    'USub': UnOp.USub
}


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


def build_tree(ast_tree):
    """
    Copies ast.

    :param ast_tree:    Built-in abstract syntax tree.
    :type ast_tree:     ast.Module
    :return:            Rebuilt abstract syntax tree.
    :rtype:             Tree
    """

    # Create fictitious root node
    custom_tree_root = Node(None)

    df_walk(ast_tree, custom_tree_root)

    # Remove fictitious root node
    if len(custom_tree_root.children) > 0:
        custom_tree_root = custom_tree_root.children[0]

    return Tree(custom_tree_root)
