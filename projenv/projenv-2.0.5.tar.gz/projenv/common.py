'''
Created on Mar 22, 2017

@author: arnon
'''

PROJENV_PREFIX='PROJENV_PREFIX'

from projenv.main import Environ

def get_proenv_prefix(env):
    try: prefix=env[PROJENV_PREFIX]
    except KeyError: prefix=None
    return prefix

def get_environ(path, osenv=True):
    environ=Environ(osenv=osenv)
    environ.loads(path=path)
    return environ