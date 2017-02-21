from os                 import path

from experipy.utils     import Namespace
from experipy.grammar   import Executable, Wrapper, Group, tokens

from .environment       import Env

########## Constants and helper functions ##########

Marena = Namespace("Marena",
    path = "marena",
    exe  = "marena",
    lib  = "libmarena.so",
)

def marenapath():
    return path.join(Env.projdir, Marena.path)

####################################################

def marena(wrapped, hotapfile=None, opts=None, 
           libmarena=path.join(marenapath(), Marena.lib), **kwargs):
        
    if opts == None:
        opts = []

    if hotapfile:
        opts.extend(["-f", hotapfile])

    return Wrapper(
        path.join(marenapath(), Marena.exe),
        ["-l ", libmarena] + opts + ["--", tokens.wrapped], 
        wrapped, **kwargs
    )

