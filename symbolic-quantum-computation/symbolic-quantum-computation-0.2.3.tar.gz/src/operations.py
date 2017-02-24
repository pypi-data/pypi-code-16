from enum import Enum


# Enum of possible binary operations.
class BinOp(Enum):
    Add = 1
    Sub = 2
    Mult = 3
    Div = 4
    Pow = 5


# Enum of possible unary operations.
class UnOp(Enum):
    UAdd = 1
    USub = 2


# Correspondence between custom and ast available binary operations
ast_bin_ops = {
    'Add': BinOp.Add,
    'Sub': BinOp.Sub,
    'Mult': BinOp.Mult,
    'Div': BinOp.Div,
    'Pow': BinOp.Pow
}

# Correspondence between custom and ast available unary operations
ast_un_ops = {
    'UAdd': UnOp.UAdd,
    'USub': UnOp.USub
}
