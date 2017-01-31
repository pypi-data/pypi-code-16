from os import getenv
from experipy.utils import Namespace

projectdir = getenv("XPS_PROJDIR", "")
if not projectdir:
    projectdir = raw_input("XPS_PROJDIR not set, provide the project directory path\n>>> ")

resultdir = getenv("XPS_VOLDIR", "")
if not resultdir:
    resultdir = raw_input("XPS_VOLDIR not set, provide the result directory path\n>>> ")

Env = Namespace(
    projdir = projectdir,
    resdir  = resultdir,
)
