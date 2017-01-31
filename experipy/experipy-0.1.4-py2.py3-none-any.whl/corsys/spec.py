from os                 import path

from experipy.utils     import Namespace
from experipy.grammar   import Executable

from .environment       import Env

########## Constants and helper functions ##########

Spec = Namespace("Spec",
    path = "benchmarks/cpu2006",
)

def specpath():
    return path.join(Env.projdir, Spec.path)

####################################################

class SpecBench(Executable):
    pass
