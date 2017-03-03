#!/usr/bin/env python
# coding=utf-8

"""
The Mal Language Parser and Runtime Enviroment main runner
"""
from __future__ import print_function
import sys
from random import shuffle

import malpy.parser
import malpy.runner


def main():
    """
    main runner
    :return:
    """
    parser = malpy.parser.Parser()
    runner = malpy.runner.Runner()
    for arg in sys.argv[1:]:
        memory = list(range(64))
        shuffle(memory)
        token_ast = parser.parse(open(arg).read())
        print(token_ast)
        if not any([token[0] == 'E' for token in token_ast]):
            output = runner.run(token_ast, memory)
            print(output)


if __name__ == '__main__':
    sys.exit(main())
