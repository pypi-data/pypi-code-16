from enum import Enum
import copy
import math

from sqc.src.Operand import Operand


# Enum of possible binary operations.
class BinOp(Enum):
    Add = 1
    Sub = 2
    Mult = 3
    Div = 4
    Pow = 5
    log = 6
    mod = 7


class Compare(Enum):
    Eq = 1
    NotEq = 2
    Lt = 3
    LtE = 4
    Gt = 5
    GtE = 6


class VectorBinOp(Enum):
    Add = 1
    Sub = 2
    MultByNum = 3
    DotProd = 4
    GetInd = 5
    Mult = 6
    TensMult = 7


# Enum of possible unary operations.
class UnOp(Enum):
    UAdd = 1
    USub = 2
    sin = 3
    cos = 4
    tg = 5
    ctg = 6
    exp = 7
    abs = 8
    arcsin = 9
    arccos = 10
    arctg = 11
    sinh = 12
    cosh = 13
    tgh = 14
    ctgh = 15
    arcctg = 16
    ln = 17
    log2 = 18
    log10 = 19
    arcsinh = 20
    arccosh = 21
    arctgh = 22


class VectorUnOp(Enum):
    USub = 1
    Transpose = 2


class VectorOp(Enum):
    Vector = 1


# Correspondence between custom and ast available binary operations
ast_bin_ops = {
    'Add': BinOp.Add,
    'Sub': BinOp.Sub,
    'Mult': BinOp.Mult,
    'Div': BinOp.Div,
    'Pow': BinOp.Pow,
    'log': BinOp.log,
    'mod': BinOp.mod,
    'vAdd': VectorBinOp.Add,
    'vSub': VectorBinOp.Sub,
    'vMulNum': VectorBinOp.MultByNum,
    'vDP': VectorBinOp.DotProd,
    'vGet': VectorBinOp.GetInd,
    'vMul': VectorBinOp.Mult,
    'vTMul': VectorBinOp.TensMult
}

ast_compare_ops = {
    'Eq': Compare.Eq,
    'NotEq': Compare.NotEq,
    'Lt': Compare.Lt,
    'LtE': Compare.LtE,
    'Gt': Compare.Gt,
    'GtE': Compare.GtE
}

functions = {
    UnOp.sin,
    UnOp.cos,
    UnOp.tg,
    UnOp.ctg,
    UnOp.exp,
    UnOp.abs,
    UnOp.sinh,
    UnOp.cosh,
    UnOp.tgh,
    UnOp.ctgh,
    UnOp.arcsin,
    UnOp.arccos,
    UnOp.arctg,
    UnOp.arcctg,
    UnOp.ln,
    UnOp.log2,
    UnOp.log10,
    BinOp.log,
    BinOp.mod,
    UnOp.arcsinh,
    UnOp.arccosh,
    UnOp.arctgh,
    VectorBinOp.Add,
    VectorBinOp.Sub,
    VectorBinOp.MultByNum,
    VectorBinOp.DotProd,
    VectorBinOp.TensMult,
    VectorBinOp.Mult,
    VectorUnOp.USub,
    VectorUnOp.Transpose
}


# Correspondence between custom and ast available unary operations
ast_un_ops = {
    'UAdd': UnOp.UAdd,
    'USub': UnOp.USub,
    'sin': UnOp.sin,
    'cos': UnOp.cos,
    'tg': UnOp.tg,
    'ctg': UnOp.ctg,
    'exp': UnOp.exp,
    'abs': UnOp.abs,
    'sinh': UnOp.sinh,
    'cosh': UnOp.cosh,
    'tgh': UnOp.tgh,
    'ctgh': UnOp.ctgh,
    'arcsin': UnOp.arcsin,
    'arccos': UnOp.arccos,
    'arctg': UnOp.arctg,
    'arcctg': UnOp.arcctg,
    'ln': UnOp.ln,
    'log2': UnOp.log2,
    'log10': UnOp.log10,
    'arcsinh': UnOp.arcsinh,
    'arccosh': UnOp.arccosh,
    'arctgh': UnOp.arctgh,
    'vUSub': VectorUnOp.USub,
    'vT': VectorUnOp.Transpose
}


oper_symbols = {
    BinOp.Add: '+',
    BinOp.Sub: '-',
    BinOp.Mult: '*',
    BinOp.Div: '/',
    BinOp.Pow: '**',
    UnOp.UAdd: '+',
    UnOp.USub: '-',
    UnOp.sin: 'sin',
    UnOp.cos: 'cos',
    UnOp.tg: 'tg',
    UnOp.ctg: 'ctg',
    UnOp.exp: 'exp',
    UnOp.abs: 'abs',
    UnOp.sinh: 'sinh',
    UnOp.cosh: 'cosh',
    UnOp.tgh: 'tgh',
    UnOp.ctgh: 'ctgh',
    UnOp.arcsin: 'arcsin',
    UnOp.arccos: 'arccos',
    UnOp.arctg: 'arctg',
    UnOp.arcctg: 'arcctg',
    UnOp.ln: 'ln',
    UnOp.log2: 'log2',
    UnOp.log10: 'log10',
    BinOp.log: 'log',
    BinOp.mod: 'mod',
    UnOp.arcsinh: 'arcsinh',
    UnOp.arccosh: 'arccosh',
    UnOp.arctgh: 'arctgh',
    VectorBinOp.Add: 'vAdd',
    VectorBinOp.Sub: 'vSub',
    VectorBinOp.MultByNum: 'vMulNum',
    VectorBinOp.DotProd: 'vDP',
    VectorBinOp.Mult: 'vMul',
    VectorBinOp.TensMult: 'vTMul',
    VectorUnOp.USub: 'vUSub',
    VectorUnOp.Transpose: 'vT',
    Compare.Eq: '=',
    Compare.NotEq: '!=',
    Compare.Lt: '<',
    Compare.LtE: '<=',
    Compare.Gt: '>',
    Compare.GtE: '>='
}


def raise_(ex):
    raise ex

oper_actions = {
    BinOp.Add: lambda x, y: x + y,
    BinOp.Sub: lambda x, y: x - y,
    BinOp.Mult: lambda x, y: x * y,
    BinOp.Div: lambda x, y: x / y if y != 0 else raise_(ZeroDivisionError),
    BinOp.Pow: lambda x, y: x ** y,
    UnOp.sin: lambda x: math.sin(x),
    UnOp.cos: lambda x: math.cos(x),
    UnOp.abs: lambda x: math.fabs(x),
    UnOp.tg: lambda x: math.tan(x),
    UnOp.ctg: lambda x: 1.0/math.tan(x),
    UnOp.exp: lambda x: math.exp(x),
    UnOp.sinh: lambda x: math.sinh(x),
    UnOp.cosh: lambda x: math.cosh(x),
    UnOp.tgh: lambda x: math.tanh(x),
    UnOp.ctgh: lambda x: 1.0/math.tanh(x),
    UnOp.arcsin: lambda x: math.asin(x),
    UnOp.arccos: lambda x: math.acos(x),
    UnOp.arctg: lambda x: math.atan(x),
    UnOp.arcctg: lambda x: math.pi/2-math.atan(x),
    UnOp.arcsinh: lambda x: math.asinh(x),
    UnOp.arccosh: lambda x: math.acosh(x),
    UnOp.arctgh: lambda x: math.atanh(x),
    UnOp.log2: lambda x: math.log2(x),
    UnOp.log10: lambda x: math.log10(x),
    UnOp.ln: lambda x: math.log(x),
    BinOp.log: lambda x, y: math.log(x, y),
    BinOp.mod: lambda x, y: x % y
}


def vector_bin_op_add(node1, node2):
    from sqc.src.Node import Node, NodeValue

    if not (node1.value.is_operation() and node1.value.operation == VectorOp.Vector and
            node2.value.is_operation() and node2.value.operation == VectorOp.Vector and
            node1.value.shape == node2.value.shape):
        raise ValueError('Vector addition error')

    new_node = Node(NodeValue(operation=VectorOp.Vector))
    for i in range(len(node1.children)):
        child_node1 = node1.children[i]
        child_node2 = node2.children[i]

        if child_node1.value.shape == ():
            new_node.add_child(Node(NodeValue(operand=Operand(numeric_value=child_node1.value.operand.numeric_value +
                                                                            child_node2.value.operand.numeric_value))))
        else:
            new_node.add_child(vector_bin_op_add(child_node1, child_node2))

    new_node.value.shape = node1.value.shape
    return new_node
oper_actions[VectorBinOp.Add] = vector_bin_op_add


def vector_binop_sub(node1, node2):
    new_node = vector_bin_op_add(node1, vector_un_op_u_sub(node2))
    new_node.value.shape = node1.value.shape
    return new_node
oper_actions[VectorBinOp.Sub] = vector_binop_sub


def vector_bin_op_mul_by_num(node1, node2):
    from sqc.src.Node import Node, NodeValue

    if not (node1.value.is_operation() and node1.value.operation == VectorOp.Vector and node2.value.shape == () or
            node2.value.is_operation() and node2.value.operation == VectorOp.Vector and node1.value.shape == ()):
        raise ValueError('Vector multiplication by number error')

    if node1.value.shape != ():
        node1, node2 = node2, node1

    new_node = Node(NodeValue(operation=VectorOp.Vector))
    for i in range(len(node2.children)):
        child_node = node2.children[i]

        if child_node.value.shape == ():
            new_node.add_child(Node(NodeValue(operand=Operand(numeric_value=node1.value.operand.numeric_value *
                                                                                  child_node.value.operand.numeric_value))))
        else:
            new_node.add_child(vector_bin_op_mul_by_num(node1, child_node))

    new_node.value.shape = node2.value.shape
    return new_node
oper_actions[VectorBinOp.MultByNum] = vector_bin_op_mul_by_num


def vector_bin_op_dot_product(node1, node2):
    from sqc.src.Node import Node, NodeValue

    if not (node1.value.is_operation() and node1.value.operation == VectorOp.Vector and node1.value.shape[0] == 1 and
            node2.value.is_operation() and node2.value.operation == VectorOp.Vector and node1.value.shape[0] == 1 and
            node1.value.shape == node2.value.shape):
        raise ValueError('Vector dot product error')

    if node1.children[0].value.is_operation():
        node1 = node1.children[0]
    if node2.children[0].value.is_operation():
        node2 = node2.children[0]

    val = 0
    for i in range(len(node1.children)):
        child_node1 = node1.children[i]
        child_node2 = node2.children[i]

        if child_node1.value.operand.is_numeric_value():
            val += child_node1.value.operand.numeric_value * child_node2.value.operand.numeric_value

    new_node = Node(NodeValue(operand=Operand(numeric_value=val)))
    return new_node
oper_actions[VectorBinOp.DotProd] = vector_bin_op_dot_product


def vector_bin_op_get_ind(node1, node2):
    from sqc.src.Node import Node, NodeValue

    if not (node1.value.is_operation() and node1.value.operation == VectorOp.Vector and node2.value.shape == ()):
        raise ValueError('Vector multiplication by number error')
    if node1.value.shape[0] == 1:
        if not (0 <= node2.value.operand.numeric_value - 1 < len(node1.children[0].children)):
            raise ValueError('Wrong index parameter')

        new_node = node1.children[0].children[node2.value.operand.numeric_value - 1]
        if new_node.value.shape != ():
            tmp_node = Node(NodeValue(operation=VectorOp.Vector))
            tmp_node.add_child(new_node)
            tmp_node.value.shape = new_node.value.shape

            new_node = tmp_node

    else:
        if not (0 <= node2.value.operand.numeric_value - 1 < len(node1.children)):
            raise ValueError('Wrong index parameter')

        new_node = node1.children[node2.value.operand.numeric_value - 1]
        if new_node.value.shape != ():
            tmp_node = Node(NodeValue(operation=VectorOp.Vector))
            tmp_node.add_child(new_node)
            tmp_node.value.shape = new_node.value.shape

            new_node = tmp_node

    if new_node.value.shape == (1, 1):
        new_node = new_node.children[0].children[0]
    return new_node

oper_actions[VectorBinOp.GetInd] = vector_bin_op_get_ind


def vector_un_op_u_sub(node):
    from sqc.src.Node import Node, NodeValue

    if not (node.value.is_operation() and node.value.operation == VectorOp.Vector):
        raise ValueError('Vector unary subtraction error')

    new_node = vector_bin_op_mul_by_num(Node(NodeValue(operand=Operand(numeric_value=-1))), node)

    new_node.value.shape = node.value.shape
    return new_node
oper_actions[VectorUnOp.USub] = vector_un_op_u_sub


def vector_un_op_transpose(node):
    from sqc.src.Node import Node, NodeValue

    if not (node.value.is_operation() and node.value.operation == VectorOp.Vector):
        raise ValueError('Vector transpose error')

    new_node = Node(NodeValue(operation=VectorOp.Vector))
    for i in range(node.value.shape[1]):
        new_node.add_child(Node(NodeValue(operation=VectorOp.Vector, shape=(1, node.value.shape[0]))))
    for i in range(node.value.shape[0]):
        for j in range(node.value.shape[1]):
            new_node.children[j].add_child(copy.copy(node.children[i].children[j]))

    new_node.value.shape = (node.value.shape[1], node.value.shape[0])
    return new_node
oper_actions[VectorUnOp.Transpose] = vector_un_op_transpose


def vector_bin_op_mul(node1, node2):
    from sqc.src.Node import Node, NodeValue

    if not (node1.value.is_operation() and node1.value.operation == VectorOp.Vector and
            node2.value.is_operation() and node2.value.operation == VectorOp.Vector and
            node1.value.shape[1] == node2.value.shape[0]):
        raise ValueError('Vector multiplication error')

    new_node = Node(NodeValue(operation=VectorOp.Vector))
    for i in range(node1.value.shape[0]):
        new_node.add_child(Node(NodeValue(operation=VectorOp.Vector, shape=(1, node2.value.shape[1]))))

    node2_t = vector_un_op_transpose(node2)

    for i in range(node1.value.shape[0]):
        for j in range(node2_t.value.shape[0]):
            new_node.children[i].add_child(vector_bin_op_dot_product(node1.children[i], node2_t.children[j]))

    new_node.value.shape = (node1.value.shape[0], node2.value.shape[1])

    if new_node.value.shape == (1, 1):
        new_node = new_node.children[0].children[0]
    return new_node
oper_actions[VectorBinOp.Mult] = vector_bin_op_mul


def vector_bin_op_tens_mul(node1, node2):
    from sqc.src.Node import Node, NodeValue

    if not (node1.value.is_operation() and node1.value.operation == VectorOp.Vector and
            node2.value.is_operation() and node2.value.operation == VectorOp.Vector):
        raise ValueError('Vector tensor multiplication error')

    new_node = Node(NodeValue(operation=VectorOp.Vector))
    for i in range(node1.value.shape[0]*node2.value.shape[0]):
        new_node.add_child(
            Node(NodeValue(operation=VectorOp.Vector, shape=(1, node1.value.shape[1]*node2.value.shape[1])))
        )

    for i1 in range(node1.value.shape[0]):
        for j1 in range(node1.value.shape[1]):
            for i2 in range(node2.value.shape[0]):
                for j2 in range(node2.value.shape[1]):
                    new_node.children[i1*node2.value.shape[0] + i2].add_child(Node(NodeValue(
                        operand=Operand(numeric_value=
                                        node1.children[i1].children[j1].value.operand.numeric_value*
                                        node2.children[i2].children[j2].value.operand.numeric_value
                                        )
                    )))

    new_node.value.shape = (node1.value.shape[0]*node2.value.shape[0],
                            node1.value.shape[1]*node2.value.shape[1])

    if new_node.value.shape == (1, 1):
        new_node = new_node.children[0].children[0]
    return new_node
oper_actions[VectorBinOp.TensMult] = vector_bin_op_tens_mul
