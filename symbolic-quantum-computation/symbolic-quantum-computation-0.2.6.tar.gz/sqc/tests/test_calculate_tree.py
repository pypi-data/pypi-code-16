import unittest

from sqc.src.Tree import Tree


class Test(unittest.TestCase):
    def test_empty(self):
        input_string = ''
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '')

    def test_binary_op_sum(self):
        input_string = '1+1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '2\n')

    def test_binary_op_sub(self):
        input_string = '1-1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '0\n')

    def test_binary_op_mul(self):
        input_string = '1*1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '1\n')

    def test_binary_op_div(self):
        input_string = '1/1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '1.0\n')

    def test_binary_op_pow(self):
        input_string = '1**1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '1\n')

    def test_two_ops(self):
        input_string = '1+1+1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '3\n')

    def test_two_ops2(self):
        input_string = '1+1-1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '1\n')

    def test_three_ops(self):
        input_string = '1/1*1-1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '0.0\n')

    def test_order_ops1(self):
        input_string = '1*2/8*4'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '1.0\n')

    def test_order_ops2(self):
        input_string = '1+2*3/4-5'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '-2.5\n')

    def test_order_pow(self):
        input_string = '1**2*3'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '3\n')

    def test_parentheses(self):
        input_string = '(1+1)*(2+2)/(3-4)+(5*6)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '22.0\n')

    def test_functions(self):
        input_string = 'mod(5,3)+log2(2)+log10(10)+log(3,3)+sin(arcsin(1))+cos(arccos(1))+tg(arctg(1))+ctg(arcctg(1))+exp(0)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, '10.0\n')

    def test_functions2(self):
        input_string = 'sinh(arcsinh(1))+cosh(arccosh(1))+tgh(arctgh(z))+ctgh(x)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, 'Add\n\tAdd\n\t\t2.0\n\t\ttgh\n\t\t\tarctgh\n\t\t\t\tz\n\tctgh\n\t\tx\n')

    def test_with_args(self):
        input_string = '2+3+x'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, 'Add\n\t5\n\tx\n')

    def test_with_args2(self):
        input_string = 'a*b/a'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = str(tree)
        self.assertEquals(output_string, 'Div\n\tMult\n\t\ta\n\t\tb\n\ta\n')

if __name__ == '__main__':
    unittest.main()
