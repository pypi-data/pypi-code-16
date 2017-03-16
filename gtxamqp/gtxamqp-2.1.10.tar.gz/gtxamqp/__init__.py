from os import pardir
from os.path import dirname, join

with open(join(dirname(__file__), pardir, "VERSION"), 'r') as f:
    __version__ = f.read()

