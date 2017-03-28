import unittest

from sqc.src.Tree import Tree, Rules


class Test(unittest.TestCase):
    def test_empty_expression(self):
        input_string = ''
        tree = Tree(expression=input_string)
        rules = Rules()
        result = rules.get_possible_rules(tree.root, tree)
        output_string = str(len(result))
        self.assertEquals(output_string, '0')

    def test1(self):
        input_string = '(a+a)/2'
        tree = Tree(expression=input_string)
        rules = Rules()
        result = rules.get_possible_rules(tree.root, tree)
        output_string = str(len(result))
        self.assertEquals(output_string, '3')

        tree, rule, id = result[0]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a/2)+(a/2)')

        tree, rule, id = result[1]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a+a)/2')

        tree, rule, id = result[2]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(2*a)/2')

    def test2(self):
        input_string = 'a*1/a'
        tree = Tree(expression=input_string)
        rules = Rules()
        result = rules.get_possible_rules(tree.root, tree)
        output_string = str(len(result))
        self.assertEquals(output_string, '3')

        tree, rule, id = result[0]
        output_string = tree.to_expression()
        self.assertEquals(output_string, 'a*(1/a)')

        tree, rule, id = result[1]
        output_string = tree.to_expression()
        self.assertEquals(output_string, 'a/a')

        tree, rule, id = result[2]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(1*a)/a')

    def test3(self):
        input_string = 'a+b-b'
        tree = Tree(expression=input_string)
        rules = Rules()
        result = rules.get_possible_rules(tree.root, tree)
        output_string = str(len(result))
        self.assertEquals(output_string, '3')

        tree, rule, id = result[0]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a+b)+(-b)')

        tree, rule, id = result[1]
        output_string = tree.to_expression()
        self.assertEquals(output_string, 'a+(b-b)')

        tree, rule, id = result[2]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(b+a)-b')

    def test4(self):
        input_string = 'a*b/a'
        tree = Tree(expression=input_string)
        rules = Rules()
        result = rules.get_possible_rules(tree.root, tree)
        output_string = str(len(result))
        self.assertEquals(output_string, '2')

        tree, rule, id = result[0]
        output_string = tree.to_expression()
        self.assertEquals(output_string, 'a*(b/a)')

        tree, rule, id = result[1]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(b*a)/a')

    def test5(self):
        input_string = 'b/a*a/b'
        tree = Tree(expression=input_string)
        rules = Rules()
        result = rules.get_possible_rules(tree.root, tree)
        output_string = str(len(result))
        self.assertEquals(output_string, '2')

        tree, rule, id = result[0]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(b/a)*(a/b)')

        tree, rule, id = result[1]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a*(b/a))/b')

    def test6(self):
        input_string = '(a*(b+c))/(c+2*b-b)'
        tree = Tree(expression=input_string)
        rules = Rules()
        result = rules.get_possible_rules(tree.root, tree)
        output_string = str(len(result))
        self.assertEquals(output_string, '8')

        tree, rule, id = result[0]
        output_string = tree.to_expression()
        self.assertEquals(output_string, 'a*((b+c)/((c+(2*b))-b))')

        tree, rule, id = result[1]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '((a*b)+(a*c))/((c+(2*b))-b)')

        tree, rule, id = result[2]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '((b+c)*a)/((c+(2*b))-b)')

        tree, rule, id = result[3]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a*(c+b))/((c+(2*b))-b)')

        tree, rule, id = result[4]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a*(b+c))/((c+(2*b))+(-b))')

        tree, rule, id = result[5]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a*(b+c))/(c+((2*b)-b))')

        tree, rule, id = result[6]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a*(b+c))/(((2*b)+c)-b)')

        tree, rule, id = result[7]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(a*(b+c))/((c+(b*2))-b)')

    def test7(self):
        input_string = '(b*b+b)/(b+1)'
        tree = Tree(expression=input_string)
        rules = Rules()
        result = rules.get_possible_rules(tree.root, tree)
        output_string = str(len(result))
        self.assertEquals(output_string, '7')

        tree, rule, id = result[0]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '((b*b)/(b+1))+(b/(b+1))')

        tree, rule, id = result[1]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(b+(b*b))/(b+1)')

        tree, rule, id = result[2]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(b*(b+1))/(b+1)')

        tree, rule, id = result[3]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(b*(b+1))/(b+1)')

        tree, rule, id = result[4]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '((b*b)+b)/(b+1)')

        tree, rule, id = result[5]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '((b**2)+b)/(b+1)')

        tree, rule, id = result[6]
        output_string = tree.to_expression()
        self.assertEquals(output_string, '((b*b)+b)/(1+b)')
