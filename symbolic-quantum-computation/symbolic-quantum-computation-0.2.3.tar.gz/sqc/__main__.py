import ast
import argparse
from src.Tree import Tree
from test_package import test


def main():
    parser = argparse.ArgumentParser(description='Symbolic quantum expression shortener')
    parser.add_argument('-t', action='store_true', help='do unit test')
    parser.add_argument('--exp', help='Input expression without spaces')

    args = parser.parse_args()

    if args.t:
        test.run_tests()

    if args.exp is not None:
        custom_tree = Tree(expression=args.exp)
        print(custom_tree)

if __name__ == '__main__':
    main()
