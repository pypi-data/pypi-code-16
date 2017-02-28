#!/usr/bin/env python
# coding=utf-8

"""
The Mal Language Parser and Runtime Enviroment main runner
"""
import sys
import malpy.parser
from random import shuffle


def main():
    """
    main runner
    :return:
    """
    p = malpy.parser.Parser()
    for arg in sys.argv[1:]:
        # m = list(range(64))
        # shuffle(m)
        # r = malpy.runner.Runner(m)
        print(p.parse(open(arg).read()))


if __name__ == '__main__':
    sys.exit(main())
