import os
import sys

from experipy.utils import Namespace

if sys.version_info[0] == 2:
    input = raw_input

def getenv_or_prompt(name):
    val = os.getenv(name, "")
    if not val:
        val = input("Environment Variable not set: {}\n>>> ".format(name))
    return val

Env = Namespace(
    projdir = getenv_or_prompt("XPS_PROJDIR"),
    resdir  = getenv_or_prompt("XPS_VOLDIR"),
)
