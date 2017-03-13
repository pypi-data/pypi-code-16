from enum import Enum
import math


class Constant(Enum):
    i = 1
    pi = 2
    e = 3

constants = {
    'i': Constant.i,
    'pi': Constant.pi,
    'e': Constant.e
}

constant_values = {
    Constant.pi: math.pi,
    Constant.e: math.e
}

constant_symbols = {
    Constant.pi: 'pi',
    Constant.e: 'e'
}
