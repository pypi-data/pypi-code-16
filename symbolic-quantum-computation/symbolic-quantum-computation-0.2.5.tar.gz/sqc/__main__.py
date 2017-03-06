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
        isAdvanced = False
        run(args.exp, isAdvanced)
    elif args.advanced is not None:
        isAdvanced = True
        run(args.advanced, isAdvanced)
    elif args.file is not None:
        isAdvanced = False
        expression = Interface()
        expression.read_from_file(args.file, isAdvanced)
        if expression is not None:
            run(expression, isAdvanced)


if __name__ == '__main__':
    main()


def run(st, isAdvanced):
    log = open('log.txt', 'w')
    tree = Tree(expression=st)
    print('Tree:')
    print(tree)
    # log.write('Tree')
    # log.write(tree)
    tree.tree_calculate()
    print('Partially calculated expression:', tree.to_expression())
    # print('Tree walk and applying rules:')
    log.write('Partially calculated expression: ' + tree.to_expression())
    expression = Interface()
    node = tree.root
    step = 0
    while node is not None:
        step += 1
        print()
        print('STEP #' + str(step))
        log.write('\n STEP #'+str(step) + ' ')

        if not isAdvanced:
            print('Expression before applying rule on this step:', tree.to_expression())
        else:
            print('>', tree.to_expression())

        log.write(tree.to_expression())

        exists_rule = expression.write_possible_rules(node, isAdvanced)
        if exists_rule:
            tree = expression.applying_rule(node, log, isAdvanced)
            node = tree.root
        else:
            node = tree.next_node()
