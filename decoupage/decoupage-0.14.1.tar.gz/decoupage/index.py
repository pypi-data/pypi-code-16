#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
index.ini
"""

import argparse
import os
import subprocess
import sys

here = os.path.dirname(os.path.realpath(__file__))
string = (str, unicode)

def index(directory):
    return '\n'.join(['{name} = {name}'.format(name=name)
                      for name in sorted(os.listdir(directory), key=lambda name: name.lower())
                      if not name.startswith('.')])

def main(args=sys.argv[1:]):

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', help='directory')
    parser.add_argument('-o', '--output', dest='output',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='output')
    options = parser.parse_args(args)

if __name__ == '__main__':
    main()
