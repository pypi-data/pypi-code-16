import os
import sys

from sqc.src.Tree import Tree, Rules


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

    @staticmethod
    def read_from_file(file_path, is_advanced):
        if not is_advanced:
            print("Enter 'exit' command to exit")

        while not os.path.exists(file_path):
            if file_path == "exit":
                return None

            print("can not open file. Try again")
            file_path = input()

        file = open(file_path, 'r')
        expression = file.read()
        file.close()

        """Alternative method

        ok = False
        while (not ok):
            try:
                file = open(file_path, 'r')
            except IOError as e:
                if file_path == "exit":
                    return None

                print("can not open file. Try again")
                file_path = input()
            else:
                expression = file.read()
                file.close()
                ok = True
        """
        return expression

    '''
    def write_expression(self, expression):
        if not is_advanced:
            print("Enter 'exit' command to exit")

        print("Do you want to read the expression from the file? (y/n)")

        # if we will need more variants i'll chose this interface
        #
        # print("Press 1-3")
        # print("1. read expression from file")
        # print("2. read expression from console")
        # print("3. exit")

        ok = False
        while not ok:
            answer = input().lower()
            if answer == 'y' or answer == 'yes':
                print("Enter the path to your file:")
                file_path = input()

                while not os.path.exists(file_path):
                    print("path does not exists. Try again")
                    file_path = input()

                file = open(file_path, 'w')
                file.write(expression)
                file.close()

                """Alternative method

                ok1 = False
                while (not ok1):
                    try:
                        file = open(file_path, 'r')
                    except IOError as e:
                        print("path does not exists. Try again")
                        file_path = input()
                    else:
                        file.write(expression)
                        file.close()
                        ok1 = True
                """
                ok = True
            elif answer == "n" or answer == "no":
                print(expression)
                ok = True
            elif answer == "exit":
                # ok = True
                return
            elif os.path.exists(answer):
                file = open(answer, 'w')
                file.write(expression)
                file.close()
                ok = True
            else:
                print("Error! Try again")

    def exp_to_ast(self, expression):
        return ast.parse(expression)

    def ast_to_exp(self, _ast):
        return ast.dump(_ast)

    def tree_to_exp(self, tree):
        return tree.__str__()
    '''

    def write_possible_rules(self, tree, is_advanced):
        rules = Rules()
        if not is_advanced:
            print("Choose the rule:")
        if self.step > 0:
            print('-1. Back')
        print('0. Exit')
        possible_rules = rules.get_possible_rules(tree.root, tree)
        print()
        num = 1
        for tree, rule in possible_rules:
            self.data[num] = (tree, rule)
            if not is_advanced:
                print(str(num) + '. Rule:', rule[0].to_expression(), '=', rule[1].to_expression())
                print('Expression after applying this rule:', tree.to_expression())
            else:
                print(str(num) + '. >', rule[0].to_expression(), '=', rule[1].to_expression(), '|',
                      tree.to_expression())
            num += 1

        self.max_rules = num-1
        return num > 0

    def applying_rule(self, log, is_advanced):
        ok = False
        while not ok:
            answer = input()
            try:
                answer = int(answer)
            except IOError:
                print('Error. Try again')
            else:
                if answer == 0:
                    print('Step-by-step solution saved in file log.txt')
                    log.close()
                    sys.exit()
                if answer == -1 and self.step > 0:
                    self.trees_on_steps.remove(self.trees_on_steps[self.step])
                    self.step -= 1
                    return self.trees_on_steps[self.step]
                elif 0 < answer <= self.max_rules:
                    current_tree, current_rule = self.data[answer]
                    if not is_advanced:
                        print('Leave your note for this step: ')
                    else:
                        print('note: ')

                    note = input()
                    if note is not None:
                        log.write('  # ' + note)
                    self.trees_on_steps.append(current_tree)
                    self.step += 1
                    return current_tree
                else:
                    print('There are only', self.max_rules, 'rules. Try again.')
