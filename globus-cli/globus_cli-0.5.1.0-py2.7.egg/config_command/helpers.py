import os
from configobj import ConfigObj


def load_config(system=False):
    if system:
        path = '/etc/globus.cfg'
    else:
        path = os.path.expanduser("~/.globus.cfg")

    return ConfigObj(path)
