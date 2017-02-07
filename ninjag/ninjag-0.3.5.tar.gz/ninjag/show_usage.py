from .tk import ioTK
import os


def show_usage():
    here = os.path.dirname(os.path.realpath(__file__))
    f_usage = os.path.join(here, 'usage.txt')
    print(ioTK.read_all(f_usage))
