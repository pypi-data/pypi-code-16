"""
    experipy.system
    ~~~~~~~~~~~~~~~

    This module provides a number of system and shell tools for helping to
    specify common tasks within the experipy grammar.
"""
from os         import path

from .grammar   import Executable

def cd(dirname):
    return Executable("cd", [dirname])


def cp(target, dest, opts=[]):
    return Executable("cp", opts + ['-t', dest, target])


def mkdir(dirname, make_parents=False):
    opts = []
    if make_parents:
        opts.append("--parents")
    return Executable("mkdir", opts + [dirname])


def mkfifo(pipename):
    return Executable("mkfifo", [pipename])


def rm(*files):
    return Executable("rm", ["-rf"] + list(files))


def wait():
    return Executable("wait")


def python_script(script, sopts=[], pythonexe="python", **kwargs):
    if 'inputs' in kwargs:
        kwargs['inputs'].append(path.abspath(script))
    else:
        kwargs['inputs'] = [path.abspath(script)]

    return Executable(pythonexe, [script] + sopts, **kwargs)


def java_app(jarfile, popts=[], javaexe="java", jopts=[], **kwargs):
    jarfile = path.abspath(jarfile)
    return Executable(javaexe, jopts + ["-jar", jarfile] + popts, **kwargs)
