import argparse

from termcolor import colored

from sqc.src.Tree import Tree
from sqc.test_package import test

from sqc.src.interface import Interface
from sqc.src.operations import oper_symbols


def run(st, is_advanced=False):
    log = open('log.txt', 'w')

    variable_shapes = Interface.get_variable_shapes()
    tree = Tree(var_shapes=variable_shapes, expression=st)
    expression = Interface(tree=tree)

    step = 0
    while tree is not None:
        if tree.root is None:
            break

        step += 1
        print()
        print('STEP ' + str(step))
        log.write('\n STEP ' + str(step) + ' ')

        if st.find('/0') >= 0 or st.find('%0') >= 0:
            print(colored('Zero division. Try again:', 'red'))
            answer = input()
            if answer == '0' or answer == 'exit':
                tree = None
            else:
                variable_shapes = Interface.get_variable_shapes()
                tree = Tree(expression=answer, var_shapes=variable_shapes)

            expression = Interface(tree=tree)
            step = 0
            continue

        try:
            tree.tree_calculate()
        except ZeroDivisionError:
            print(colored('Zero division. Try again:', 'red'))
            answer = input()
            if answer == '0' or answer == 'exit':
                tree = None
            else:
                variable_shapes = Interface.get_variable_shapes()
                tree = Tree(expression=answer, var_shapes=variable_shapes)

            expression = Interface(tree=tree)
            step = 0
            continue

        print('Tree:')
        print(tree)

        # log.write('Tree:')
        # log.write(tree)

        if not is_advanced:
            print(expression.show_last_k_trees())
            # print('Expression before applying rule on this step:' + oper_symbols[tree.action], tree.to_expression())
        else:
            print('>', tree.to_expression())

        log.write(tree.to_expression())

        exists_rule = expression.write_possible_rules(tree, is_advanced)
        if exists_rule is None:
            print('Try again:')
        elif not exists_rule:
            print('No possible rules. You can write new expression:')

        tree, new = expression.apply_rule(log, is_advanced)
        if new:
            expression = Interface(tree=tree)
            st = tree.to_expression()
            variable_shapes = expression.get_variable_shapes()
            tree = Tree(expression=st, var_shapes=variable_shapes)
            step = 0


def main():
    parser = argparse.ArgumentParser(description='Symbolic quantum expression shortener')
    parser.add_argument('-t', action='store_true', help='do unit test')
    parser.add_argument('--exp', help='Run program. Argument must be expression without spaces, with quotes')
    parser.add_argument('--f', help='Read expressions from your file.')
    parser.add_argument('-m', action='store_true', help='Advanced mode. Only if you know what is it.')

    args = parser.parse_args()

    if args.t:
        test.run_tests()
    elif args.exp is not None:
        run(args.exp, args.m)
    elif args.f is not None:
        expression = Interface()
        expression.read_from_file(args.f, args.m)
        if expression is not None:
            for exp in expression.data:
                run(exp, args.m)
            else:
                print(colored('File is empty', 'red'))

            expression.data.close()
    else:
        expression = input()
        run(st=expression, is_advanced=args.m)

if __name__ == '__main__':
    main()


