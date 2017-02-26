import argparse
from src.Tree import Tree, Rules
from test_package import test


def main():
    parser = argparse.ArgumentParser(description='Symbolic quantum expression shortener')
    parser.add_argument('-t', action='store_true', help='do unit test')
    parser.add_argument('--exp', help='Input expression without spaces')

    args = parser.parse_args()

    if args.t:
        test.run_tests()

    if args.exp is not None:
        tmp(args.exp)

if __name__ == '__main__':
    main()


def tmp(st):
    tree = Tree(expression=st)
    print('Tree:')
    print(tree)

    tree.tree_calculate()
    print('Partially calculated expression:', tree.to_expression())

    print()
    print('Tree walk and applying rules:')
    node = tree.root
    rules = Rules()
    while node is not None:
        i = 0
        for rule in rules:
            i += 1
            if node.unify(rule[0].root) is not None:
                print()
                print('rewrite possible using rule #', i)
                tmp_tree = Tree(root=node).get_copy()
                print('before:', tmp_tree.to_expression())
                tmp_tree.root.replace(rule)
                print('after:', tmp_tree.to_expression())

        node = tree.next_node()

# tmp('(x+1)*(y+1)+(x+1)*z')
