import unittest
from src.Tree import Tree


class Test(unittest.TestCase):
    def test_empty_expression(self):
        input_string = ''
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_unary_op(self):
        input_string = '+1'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_binary_op_sum(self):
        input_string = '1+1'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_binary_op_sub(self):
        input_string = '1-1'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_binary_op_mul(self):
        input_string = '1*1'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_binary_op_div(self):
        input_string = '1/1'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_binary_op_pow(self):
        input_string = '1**1'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_two_ops(self):
        input_string = '1+1+1'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_three_ops(self):
        input_string = '1/1*1-1'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_order_ops1(self):
        input_string = '1*2/3*4'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_order_ops2(self):
        input_string = '1+2*3/4-5'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_order_pow(self):
        input_string = '1**2*3'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_parentheses(self):
        input_string = '(1+1)*(2+2)/(3-4)+(5*6)'
        self.assertEquals(Tree(expression=input_string), Tree(expression=input_string))

    def test_not_equal1(self):
        input_string1 = '1+1'
        input_string2 = '1+2'
        self.assertNotEquals(Tree(expression=input_string1), Tree(expression=input_string2))

    def test_not_equal2(self):
        input_string1 = '1+1'
        input_string2 = '1*1'
        self.assertNotEquals(Tree(expression=input_string1), Tree(expression=input_string2))

    def test_not_equal3(self):
        input_string1 = '+1'
        input_string2 = '1'
        self.assertNotEquals(Tree(expression=input_string1), Tree(expression=input_string2))

    def test_not_equal4(self):
        input_string1 = '1*(1+1)'
        input_string2 = '(1+1)*1'
        self.assertNotEquals(Tree(expression=input_string1), Tree(expression=input_string2))

if __name__ == '__main__':
    unittest.main()
