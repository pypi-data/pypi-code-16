import redis

from .foorti_systems import *
from .foorti_list import List

def fetch_list(name, system='default'):
    return List(name, system)
