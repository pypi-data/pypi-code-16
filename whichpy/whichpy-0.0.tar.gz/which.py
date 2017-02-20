#!/usr/bin/env python

import os
import sys

def which(fileName, path=os.environ['PATH']):
    """python equivalent of which; should really be in the stdlib"""
    dirs = path.split(os.pathsep)
    for dir in dirs:
        if os.path.isfile(os.path.join(dir, fileName)):
            return os.path.join(dir, fileName)
        if os.path.isfile(os.path.join(dir, fileName + ".exe")):
            return os.path.join(dir, fileName + ".exe")

def main(args=sys.argv[1:]):
    """CLI"""
    for i in sys.argv[1:]:
        print which(i)

if __name__ == '__main__':
    main()
