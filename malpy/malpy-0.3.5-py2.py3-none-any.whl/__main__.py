#!/usr/bin/env python
# coding=utf-8

"""
The Mal Language Parser and Runtime Enviroment main runner
"""
from __future__ import print_function
import sys

import malpy.parser
import malpy.runner


def main():
    """
    main runner
    :return: None
    """
    parser = malpy.parser.Parser()
    runner = malpy.runner.Runner()
    for arg in sys.argv[1:]:
        memory = [0]*64
        token_ast = parser.parse(open(arg).read())
        print(token_ast)
        if not any([token[0] == 'E' for token in token_ast]):
            output = runner.run(token_ast, memory)
            print(output)


if __name__ == '__main__':
    sys.exit(main())
