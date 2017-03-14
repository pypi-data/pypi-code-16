import argparse
import os

from sqc.src.Tree import Tree
from sqc.test_package import test

from sqc.src.interface import Interface


def main():
    parser = argparse.ArgumentParser(description='Symbolic quantum expression shortener')
    parser.add_argument('-t', action='store_true', help='do unit test')
    parser.add_argument('--exp', help='Input expression without spaces')
    parser.add_argument('--file', help='Input path to the file. Expression in file must be written without spaces')
    parser.add_argument('--advanced', help='Advanced mode. Only if you know what is it.')
    # parser.add_argument('--rules', help='Edit rules mode.')
    args = parser.parse_args()

    if args.t:
        test.run_tests()

    if args.exp is not None:
        is_advanced = False
        run(args.exp, is_advanced)
    elif args.advanced is not None:
        is_advanced = True
        run(args.advanced, is_advanced)
    elif args.file is not None:
        is_advanced = False
        expression = Interface()
        expression.read_from_file(args.file, is_advanced)
        if expression is not None:
            run(expression, is_advanced)


if __name__ == '__main__':
    main()


def run(st, is_advanced):
    log = open('log.txt', 'w')
    tree = Tree(expression=st)

    # log.write('Tree')
    # log.write(tree)
    tree.tree_calculate()
    print('Partially calculated expression:', tree.to_expression())
    # print('Tree walk and applying rules:')
    log.write('Partially calculated expression: ' + tree.to_expression())
    expression = Interface(tree=tree)
    node = tree.root
    step = 0
    while node is not None:
        step += 1
        print()
        print('STEP #' + str(step))
        log.write('\n STEP #'+str(step) + ' ')

        tree.tree_calculate()

        print('Tree:')
        print(tree)

        if not is_advanced:
            print('Expression before applying rule on this step:', tree.to_expression())
        else:
            print('>', tree.to_expression())

        log.write(tree.to_expression())

        exists_rule = expression.write_possible_rules(tree, is_advanced)
        if exists_rule:
            tree = expression.applying_rule(log, is_advanced)
            node = tree.root
        else:
            node = tree.next_node()
