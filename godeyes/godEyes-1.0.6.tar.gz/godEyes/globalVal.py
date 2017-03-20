# coding:utf-8

import inspect
import os


curdir = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))

rootdir = os.path.abspath(os.path.join(curdir, os.path.pardir, os.path.pardir))

TAG = '=======>'

__version__ = '1.0.6'

def get_version():
    return __version__
    
if __name__ == '__main__':
    print get_version()