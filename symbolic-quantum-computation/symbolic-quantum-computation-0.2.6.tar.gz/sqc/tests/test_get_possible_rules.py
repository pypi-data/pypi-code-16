import unittest

from sqc.src.Tree import Tree, Rules


# class Test(unittest.TestCase):
#     def test_empty_expression(self):
#         input_string = ''
#         tree = Tree(expression=input_string)
#         rules = Rules()
#         result = rules.get_possible_rules(tree.root, tree)
#         output_string = str(len(result))
#         self.assertEquals(output_string, '0')
#
#     def test1(self):
#         input_string = '(a+a)/2'
#         tree = Tree(expression=input_string)
#         rules = Rules()
#         result = rules.get_possible_rules(tree.root, tree)
#         output_string = str(len(result))
#         self.assertEquals(output_string, '3')
#
#         tree, rule = result[0]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, '(a+c)/b=a/b+c/b')
#
#         tree, rule = result[1]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a+b=b+a')
#
#         tree, rule = result[2]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a+a=2*a')
#
#     def test2(self):
#         input_string = 'a*1/a'
#         tree = Tree(expression=input_string)
#         rules = Rules()
#         result = rules.get_possible_rules(tree.root, tree)
#         output_string = str(len(result))
#         self.assertEquals(output_string, '2')
#
#         tree, rule = result[0]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#         tree, rule = result[1]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*1=a')
#
#     def test3(self):
#         input_string = 'a+b-b'
#         tree = Tree(expression=input_string)
#         rules = Rules()
#         result = rules.get_possible_rules(tree.root, tree)
#         output_string = str(len(result))
#         self.assertEquals(output_string, '3')
#
#         tree, rule = result[0]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a-b=a+(-b)')
#
#         tree, rule = result[1]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a+b=b+a')
#
#         tree, rule = result[2]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a-a=0')
#
#     def test4(self):
#         input_string = 'a*b/a'
#         tree = Tree(expression=input_string)
#         rules = Rules()
#         result = rules.get_possible_rules(tree.root, tree)
#         output_string = str(len(result))
#         self.assertEquals(output_string, '2')
#
#         tree, rule = result[0]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#         tree, rule = result[1]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a/a=1')
#
#     def test5(self):
#         input_string = 'b/a*a/b'
#         tree = Tree(expression=input_string)
#         rules = Rules()
#         result = rules.get_possible_rules(tree.root, tree)
#         output_string = str(len(result))
#         self.assertEquals(output_string, '4')
#
#         tree, rule = result[0]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#         tree, rule = result[1]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#         tree, rule = result[2]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#         tree, rule = result[3]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#
#     def test6(self):
#         input_string = '(a*(b+c))/(c+2*b-b)'
#         tree = Tree(expression=input_string)
#         rules = Rules()
#         result = rules.get_possible_rules(tree.root, tree)
#         output_string = str(len(result))
#         self.assertEquals(output_string, '5')
#
#         tree, rule = result[0]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#         tree, rule = result[1]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a+b=b+a')
#
#         tree, rule = result[2]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a+b=b+a')
#
#         tree, rule = result[3]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#         tree, rule = result[4]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, '2*a=a+a')
#
#     def test7(self):
#         input_string = '(b*b+b)/(b+1)'
#         tree = Tree(expression=input_string)
#         rules = Rules()
#         result = rules.get_possible_rules(tree.root, tree)
#         output_string = len(result)
#         self.assertEquals(output_string, '5')
#
#         tree, rule = result[0]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, '(a+c)/b = a/b+c/b')
#
#         tree, rule = result[1]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a+b=b+a')
#
#         tree, rule = result[2]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b+a*c=a*(b+c)')
#
#         tree, rule = result[3]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a*b=b*a')
#
#         tree, rule = result[4]
#         output_string = rule[0].to_expression() + '=' + rule[1].to_expression()
#         self.assertEquals(output_string, 'a+b=b+a')
