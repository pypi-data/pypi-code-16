import sys
import ast
import argparse
from src.Tree import Tree
from test_package import test


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Symbolic quantum expression shortener')
    parser.add_argument('-t', action='store_true', help='do unit test')
    parser.add_argument('--exp', help='Input expression without spaces')

    args = parser.parse_args()

    if args.t:
        test.run_tests()

    if args.exp is not None:
        ast_tree = ast.parse(args.exp)
        custom_tree = Tree(ast_tree)
        print(custom_tree)

if __name__ == '__main__':
    main()
