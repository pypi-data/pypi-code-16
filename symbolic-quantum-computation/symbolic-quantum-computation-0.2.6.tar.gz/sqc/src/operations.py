from enum import Enum
import math
import copy

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


class VectorBinOp(Enum):
    Add = 1
    Sub = 2
    MultByNum = 3
    DotProd = 4
    GetInd = 5


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
    'vGet': VectorBinOp.GetInd
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
    VectorUnOp.USub
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
    VectorUnOp.USub: 'vUSub'
}

oper_actions = {
    BinOp.Add: lambda x, y: x + y,
    BinOp.Sub: lambda x, y: x - y,
    BinOp.Mult: lambda x, y: x * y,
    BinOp.Div: lambda x, y: x / y if y != 0 else ZeroDivisionError,
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


def VectorBinOp_Add(operand1, operand2):
    from sqc.src.Node import Node, NodeValue
    if operand1.shape != operand2.shape:
        raise ValueError('Vector addition shape error')
    new_elem_vector = []
    for i in range(len(operand1.vector_elements)):
        node1 = operand1.vector_elements[i]
        node2 = operand2.vector_elements[i]

        if node1.value.operand.shape != node2.value.operand.shape:
            raise ValueError('Vector addition shape error')

        if node1.value.operand.is_vector():
            new_elem_vector.append(VectorBinOp_Add(node1.value.operand, node2.value.operand))
        elif node1.value.operand.is_numeric_value():
            new_elem_vector.append(
                Node(
                    NodeValue(
                        operand=Operand(
                            numeric_value=node1.value.operand.numeric_value + node2.value.operand.numeric_value
                        )
                    )
                )
            )
    return Node(NodeValue(operand=Operand(vector_elements=new_elem_vector)))
oper_actions[VectorBinOp.Add] = VectorBinOp_Add


def VectorBinOp_Sub(operand1, operand2):
    from sqc.src.Node import Node, NodeValue
    if operand1.shape != operand2.shape:
        raise ValueError('Vector subtraction shape error')
    new_elem_vector = []
    for i in range(len(operand1.vector_elements)):
        node1 = operand1.vector_elements[i]
        node2 = operand2.vector_elements[i]

        if node1.value.operand.shape != node2.value.operand.shape:
            raise ValueError('Vector subtraction shape error')

        if node1.value.operand.is_vector():
            new_elem_vector.append(VectorBinOp_Sub(node1.value.operand, node2.value.operand))
        elif node1.value.operand.is_numeric_value():
            new_elem_vector.append(
                Node(
                    NodeValue(
                        operand=Operand(
                            numeric_value=node1.value.operand.numeric_value - node2.value.operand.numeric_value
                        )
                    )
                )
            )
    return Node(NodeValue(operand=Operand(vector_elements=new_elem_vector)))
oper_actions[VectorBinOp.Sub] = VectorBinOp_Sub


def VectorBinOp_MultByNum(operand1, operand2):
    from sqc.src.Node import Node, NodeValue
    new_elem_vector = []
    for i in range(len(operand2.vector_elements)):
        node = operand2.vector_elements[i]

        if node.value.operand.is_vector():
            new_elem_vector.append(VectorBinOp_MultByNum(operand1, node.value.operand))
        elif node.value.operand.is_numeric_value():
            new_elem_vector.append(
                Node(
                    NodeValue(
                        operand=Operand(
                            numeric_value=operand1.numeric_value * node.value.operand.numeric_value
                        )
                    )
                )
            )
    return Node(NodeValue(operand=Operand(vector_elements=new_elem_vector)))
oper_actions[VectorBinOp.MultByNum] = VectorBinOp_MultByNum


def VectorBinOp_DotProd(operand1, operand2):
    from sqc.src.Node import Node, NodeValue
    print(operand1.shape)
    if operand1.shape != operand2.shape or operand1.shape[0] != 1:
        raise ValueError('Vector dot product shape error')
    val = 0
    for i in range(len(operand1.vector_elements)):
        node1 = operand1.vector_elements[i]
        node2 = operand2.vector_elements[i]

        if node1.value.operand.shape != node2.value.operand.shape:
            raise ValueError('Vector dot product shape error')

        if node1.value.operand.is_numeric_value():
            val += node1.value.operand.numeric_value * node2.value.operand.numeric_value
    return Node(NodeValue(operand=Operand(numeric_value=val)))
oper_actions[VectorBinOp.DotProd] = VectorBinOp_DotProd


def VectorBinOp_GetInd(operand1, operand2):
    if not (0 <= operand2.numeric_value - 1 < len(operand1.vector_elements)):
        raise ValueError('Wrong index parameter')
    return copy.copy(operand1.vector_elements[operand2.numeric_value - 1])
oper_actions[VectorBinOp.GetInd] = VectorBinOp_GetInd


def VectorUnOp_USub(operand):
    return VectorBinOp_MultByNum(Operand(numeric_value=-1), operand)
oper_actions[VectorUnOp.USub] = VectorUnOp_USub
