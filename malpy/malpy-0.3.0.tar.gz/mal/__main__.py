#!/usr/bin/env python
# coding=utf-8

"""
The Mal Language Parser and Runtime Enviroment main runner
"""
import sys
import mal.parser
from random import shuffle


def main():
    """
    main runner
    :return:
    """
    p = mal.parser.Parser()
    for arg in sys.argv[1:]:
        # m = list(range(64))
        # shuffle(m)
        # r = mal.runner.Runner(m)
        print(p.parse(open(arg).read()))


if __name__ == '__main__':
    sys.exit(main())
