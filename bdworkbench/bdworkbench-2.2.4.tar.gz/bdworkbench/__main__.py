#!/usr/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.
#

import sys, argparse
from .bdwb import BDwb as Workbench

def main():
    parser = argparse.ArgumentParser(description='Available options')
    parser.add_argument('batchfile', metavar='INSTRUCTION_FILE', nargs='?',
                        default=None,
                        help='A file that contains workbench commands for '
                             'non-interactive processing.')
    parser.add_argument('--init', action='store_true', default=False, dest='init',
                        help='Initialize the current directory with skeletal code '
                        'and directroy structure for developing a catalog entry '
                        'for BlueData\'s EPIC platform.')
    parser.add_argument('-i', '--instruction', metavar='INSTRUCTION',
                        action='store', dest='instr', default=None,
                        help='A single instruction to execute. This will exit '
                        'as soon as the given instructions is executed.')
    args = parser.parse_args()

    if (args.instr != None) and (args.batchfile != None):
        parser.error("-i/--instruction and batchfile are mutually exclusive options.")
        sys.exit(1)

    instruction=''
    if args.init == True:
        instruction='workbench init'
    else:
        instruction=args.instr

    Workbench(instr=instruction, batchfile=args.batchfile).cmdloop()
