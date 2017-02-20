"""
Ninjag: Ninja build file generator

Usage: ninjag output.ninja in1.yaml in2.yaml ...
Author: Steven(Yuhang) Wang
License: MIT/X11
"""
import sys
from .main import main
from .show_usage import show_usage


def cli():
    if len(sys.argv) < 2:
        show_usage()
        print("Error hint: need at least one command line arguments\n")
        exit()
    else:
        main(sys.argv[1], sys.argv[2:])
