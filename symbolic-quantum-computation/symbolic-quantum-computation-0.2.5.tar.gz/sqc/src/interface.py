import os
import sys

from sqc.src.Tree import Tree, Rules


class Interface:
    def read_from_file(self, file_path, isAdvanced):
        if not isAdvanced:
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
        if not isAdvanced:
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

    def write_possible_rules(self, node, isAdvanced):
        rules = Rules()
        num = 0
        if not isAdvanced:
            print("Choose the rule:")

        print('0. Exit')
        for rule in rules:
            if node.unify(rule[0].root) is not None:
                num += 1
                tmp_tree = Tree(root=node).get_copy()
                tmp_tree.root.replace(rule)
                if not isAdvanced:
                    print(str(num)+'. Rule:', rule[0].to_expression(), '=', rule[1].to_expression())
                    print('Expression after applying this rule:', tmp_tree.to_expression())
                else:
                    print(str(num) + '. >', rule[0].to_expression(), '=', rule[1].to_expression(), '|', tmp_tree.to_expression())

        return num > 0

    def applying_rule(self, node, log, isAdvanced):
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
                elif 0 < answer:
                    rules = Rules()
                    num = 0
                    for rule in rules:
                        if node.unify(rule[0].root) is not None:
                            num += 1
                            if num == answer:
                                tmp_tree = Tree(root=node).get_copy()
                                tmp_tree.root.replace(rule)
                                # ok = True
                                if not isAdvanced:
                                    print('Leave your note for this step: ')
                                else:
                                    print('note: ')

                                note = input()
                                if note is not None:
                                    log.write('  # ' + note)

                                return tmp_tree
                    else:
                        print('There are only', num, 'rules. Try again.')