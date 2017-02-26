import unittest
from src.Tree import Tree


class Test(unittest.TestCase):
    def test_binary_op_sum(self):
        input_string = '1+1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '2')

    def test_binary_op_sub(self):
        input_string = '1-1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '0')

    def test_binary_op_mul(self):
        input_string = '1*1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '1')

    def test_binary_op_div(self):
        input_string = '1/1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '1.0')

    def test_binary_op_pow(self):
        input_string = '1**1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '1')

    def test_two_ops(self):
        input_string = '1+1+1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '3')

    def test_three_ops(self):
        input_string = '1/1*1-1'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '0.0')

    def test_order_ops1(self):
        input_string = '1*2/8*4'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '1.0')

    def test_order_ops2(self):
        input_string = '1+2*3/4-5'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '-2.5')

    def test_order_pow(self):
        input_string = '1**2*3'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '3')

    def test_parentheses(self):
        input_string = '(1+1)*(2+2)/(3-4)+(5*6)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '22.0')

    def test_with_args1(self):
        input_string = '2+3+x'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '5+x')

    def test_with_args2(self):
        input_string = 't-(3+x)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, 't-(3+x)')

    def test_with_args3(self):
        input_string = '-(1+a)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '-(1+a)')

    def test_with_args4(self):
        input_string = '(2+3+a)*(1+a)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(5+a)*(1+a)')

    def test_with_args5(self):
        input_string = '1/(3*4+b+c)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '1/(12+b+c)')

    # 2+x-2
    def test_with_args6(self):
        input_string = '2**(x-2)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '2**(x-2)')

    def test_with_args7(self):
        input_string = '+(1+3+x)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '+(4+x)')

    def test_with_args8(self):
        input_string = '2*(x)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '2*x')

    def test_with_args9(self):
        input_string = '(3*x)/3'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '3*x/3')

    def test_with_args10(self):
        input_string = '(x+1)*(1-2)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '(x+1)*(-1)')

if __name__ == '__main__':
    unittest.main()
