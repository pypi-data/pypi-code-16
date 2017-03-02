#!/usr/bin/env python
# -*- coding: utf-8 -*-
# XXX Update Docstring
"""
pyFuckery - parser.py
Created on 2/19/17.


"""
# Stdlib
import argparse
import logging
import sys

# Custom Code
from fuckery.constants import GRAMMER
# Third Party Code
from lark import Lark
from lark import Tree

log = logging.getLogger(__name__)


def parse_program(s: str) -> Tree:
    """
    Parser a program to generate the lark parse Tree.

    :param s: Brainfuck program to parse.
    :return:
    """
    brainfuck_parser = Lark(GRAMMER, start='program')
    r = brainfuck_parser.parse(s)
    return r


# noinspection PyMissingOrEmptyDocstring
def main(options):  # pragma: no cover
    if not options.verbose:
        logging.disable(logging.DEBUG)

    with open(options.input, 'rb') as f:
        buf = f.read()

    s = buf.decode()

    log.debug('Parsing: {}'.format(s))

    t = parse_program(s=s)
    print(t.pretty())

    sys.exit(0)


# noinspection PyMissingOrEmptyDocstring
def makeargpaser():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Parse a brainfuck file and print out the resulting AST.")
    parser.add_argument('-i', '--input', dest='input', required=True, type=str, action='store',
                        help='Input file to process')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                        help='Enable verbose output')
    return parser


def _main():  # pragma: no cover
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s [%(filename)s:%(funcName)s]')
    p = makeargpaser()
    opts = p.parse_args()
    main(opts)


if __name__ == '__main__':  # pragma: no cover
    _main()
