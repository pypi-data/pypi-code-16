from os                 import path

from experipy.utils     import Namespace
from experipy.grammar   import Executable, Wrapper, Group, tokens

from .environment       import Env

########## Constants and helper functions ##########

Pin = Namespace("Pin",
    path = "pin-2.14",
    exe  = "pin.sh",
)

def pinpath():
    return path.join(Env.projdir, Pin.path)

####################################################

def pintool(tool, target, popts=[], topts=[], **kwargs):
    return Wrapper(
        path.join(pinpath(), Pin.exe),
        popts + ["-t "+tool] + topts + ["--", tokens.wrapped],
        target, **kwargs
    )


def memtracer(target, popts=["-follow-execv"], topts=[], **kwargs):
    """Returns a Wrapper describing a Memtracer run"""
    outfiles = kwargs.get("outputs", [])
    outfiles.extend([
        "memtracer.out", "meminfo.txt", "malloc_trace.out",
        "ap_info.out", "ap_map.out", "pin.log"
    ])

    return pintool(
        path.join(pinpath(), "source", "tools", 
            "memtracer", "obj-intel64", "memtracer.so"
        ),
        target, popts, topts, outputs=outfiles, **kwargs
    )

