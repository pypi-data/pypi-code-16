import unittest
import ast
from src.Tree import Tree


class Test(unittest.TestCase):
    @staticmethod
    def get_output_string(input_string):
        ast_tree = ast.parse(input_string)
        custom_tree = Tree(ast_tree)
        return str(custom_tree)

    def test_empty_expression(self):
        input_string = ''
        self.assertEquals(self.get_output_string(input_string), '')

    def test_unary_op(self):
        input_string = '+1'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'UAdd\n\t1\n')

    def test_binary_op_sum(self):
        input_string = '1+1'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Add\n\t1\n\t1\n')

    def test_binary_op_sub(self):
        input_string = '1-1'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Sub\n\t1\n\t1\n')

    def test_binary_op_mul(self):
        input_string = '1*1'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Mult\n\t1\n\t1\n')

    def test_binary_op_div(self):
        input_string = '1/1'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Div\n\t1\n\t1\n')

    def test_binary_op_pow(self):
        input_string = '1**1'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Pow\n\t1\n\t1\n')

    def test_two_ops(self):
        input_string = '1+1+1'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Add\n\tAdd\n\t\t1\n\t\t1\n\t1\n')

    def test_three_ops(self):
        input_string = '1/1*1-1'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Sub\n\tMult\n\t\tDiv\n\t\t\t1\n\t\t\t1\n\t\t1\n\t1\n')

    def test_order_ops1(self):
        input_string = '1*2/3*4'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Mult\n\tDiv\n\t\tMult\n\t\t\t1\n\t\t\t2\n\t\t3\n\t4\n')

    def test_order_ops2(self):
        input_string = '1+2*3/4-5'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Sub\n\tAdd\n\t\t1\n\t\tDiv\n\t\t\tMult\n\t\t\t\t2\n\t\t\t\t3\n\t\t\t4\n\t5\n')

    def test_order_pow(self):
        input_string = '1**2*3'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Mult\n\tPow\n\t\t1\n\t\t2\n\t3\n')

    def test_parentheses(self):
        input_string = '(1+1)*(2+2)/(3-4)+(5*6)'
        output_string = self.get_output_string(input_string)
        self.assertEquals(output_string, 'Add\n\tDiv\n\t\tMult\n\t\t\tAdd\n\t\t\t\t1\n\t\t\t\t1\n\t\t\tAdd\n\t\t\t\t2\n\t\t\t\t2\n\t\tSub\n\t\t\t3\n\t\t\t4\n\tMult\n\t\t5\n\t\t6\n')


if __name__ == '__main__':
    unittest.main()
