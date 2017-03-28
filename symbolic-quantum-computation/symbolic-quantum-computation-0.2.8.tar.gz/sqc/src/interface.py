import os
import sys
import ast
from termcolor import colored

from sqc.src.Tree import Tree, Rules
from sqc.src.Constant import constants
from sqc.src.operations import Compare, oper_symbols


class Interface:
    def __init__(self, tree=None):
        self.trees_on_steps = []
        if tree is not None:
            self.trees_on_steps.append(tree)
            self.step = 0
        else:
            self.step = -1
        self.data = {}
        self.max_rules = 0

    def read_from_file(self, file_path, is_advanced=False):
        while not os.path.exists(file_path):
            if file_path == "exit":
                sys.exit()
            elif file_path == '0':
                return None

            print("Can not open file. Try again")
            if not is_advanced:
                print("Enter 'exit' command to exit")

            file_path = input()

        file = open(file_path, 'r')
        self.data = file

    @staticmethod
    def get_variable_shapes():
        print('Enter names of variables and their shapes in form')
        print('<name> <shape_tuple>')
        print('End input with empty line')

        result = {}
        line = input()
        while len(line) > 0:
            if line.find(' '):
                var, shape = line.split(' ')[0], ast.literal_eval(line.split(' ')[1])

                if var in result.keys():
                    print('Variable already defined. Try again.')
                elif not isinstance(shape, tuple):
                    print('Wrong shape type. Expected tuple. Try again.')
                elif var in constants.keys():
                    print('Variable name reserved for constant. Try again.')
                else:
                    result[var] = shape
            else:
                print('Space separated line expected. Try again.')

            line = input()

        return result

    def write_possible_rules(self, tree, is_advanced):
        if not is_advanced:
            print("Choose the rule or write new expression:")

        if self.step > 0:
            print('-1. Back')

        print('0. Exit')
        print()

        rules = Rules()
        possible_rules = rules.get_possible_rules(tree.root, tree)
        num = 1
        error = False
        possible_rules_ids = set([el[2] for el in possible_rules])
        for id in possible_rules_ids:
            current_rules = [(el[0], el[1]) for el in possible_rules if el[2] == id]
            rule = current_rules[0][1]
            if not is_advanced:
                print('Rule:', rule[0].to_expression(), oper_symbols[rule[2]], rule[1].to_expression())
            for new_tree, rule in current_rules:
                self.data[num] = (new_tree, rule)
                new_exp = new_tree.to_expression('yellow')

                if not is_advanced:
                    print(str(num) + '. Expression after applying this rule:', new_exp)
                else:
                    print(str(num) + '. >', rule[0].to_expression(), oper_symbols[rule[2]], rule[1].to_expression(), '|',
                          new_exp)

                new_exp = new_tree.to_expression()
                if new_exp.find('/0') >= 0 or new_exp.find('%0') >= 0:
                    print(colored('Zero division.', 'red'))
                    error = True
                num += 1

        self.max_rules = num - 1
        if error:
            return None
        else:
            return num > 1

    def apply_rule(self, log, is_advanced):
        ok = False
        while not ok:
            answer = input()
            if answer is not None and len(answer) > 0:
                try:
                    answer = int(answer)
                except ValueError:
                    try:  # this try is useless now
                        tree = Tree(expression=answer)
                    except ValueError:
                        raise ValueError('The expression includes unexpected symbols')
                    else:
                        if tree.root is None:
                            print('Try again:')
                        else:
                            log.write('\n\n New expression: ' + answer)
                            return tree, True
                else:
                    if answer == 0:
                        print(colored('Step-by-step solution successfully saved in file log.txt', 'green'))
                        log.close()
                        return None, False
                    if answer == -1 and self.step > 0:
                        self.trees_on_steps.remove(self.trees_on_steps[self.step])
                        self.step -= 1
                        return self.trees_on_steps[self.step], False
                    elif 0 < answer <= self.max_rules:
                        if not is_advanced:
                            print('Leave your note for this step: ')
                        else:
                            print('note: ')

                        note = input()
                        if note is not None and len(note) > 0:
                            log.write('  # ' + note)

                        current_tree, current_rule = self.data[answer]
                        if current_tree.action != Compare.Gt and current_tree.action != Compare.Lt:
                            current_tree.action = current_rule[2]
                        self.trees_on_steps.append(current_tree)
                        self.step += 1
                        return current_tree, False
                    else:
                        print(colored('There are only', self.max_rules, 'rules. Try again.', 'red'))

    def show_last_k_trees(self, k=2):
        expr = 'Expression before applying rule on this step:'
        if self.step < k:
            k = self.step+1
        for i in range(k):
            tree = self.trees_on_steps[self.step+1-k+i]
            expr += oper_symbols[tree.action] + tree.to_expression()
        return expr
