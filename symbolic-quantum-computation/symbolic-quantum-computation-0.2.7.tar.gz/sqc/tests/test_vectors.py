import unittest

from sqc.src.Tree import Tree


class Test(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(Exception):
            Tree(expression='[]')

    def test_uni_vector(self):
        input_string = '[1]'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[1]')

    def test_empty_double_vector(self):
        input_string = '[[2], [1]]'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[2], [1]]')

    def test_vector1(self):
        input_string = '[x]'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[x]')

    def test_vector2(self):
        input_string = '[x, y]'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[x, y]')

    def test_vector3(self):
        input_string = '[[1, x], [2, y]]'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[1, x], [2, y]]')

    def test_vector_ops_Add_1(self):
        input_string = 'vAdd([3], [1])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[4]')

    def test_vector_ops_Add_2(self):
        input_string = 'vAdd([3, 4], [1, 6])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[4, 10]')

    def test_vector_ops_Add_3(self):
        input_string = 'vAdd([[3]], [[1]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[4]]')

    def test_vector_ops_Add_4(self):
        input_string = 'vAdd([[3, 2]], [[1, 5]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[4, 7]]')

    def test_vector_ops_Add_5(self):
        input_string = 'vAdd([[3, 5], [1, 6], [3, 7]], [[3, 5], [1, 6], [3, 7]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[6, 10], [2, 12], [6, 14]]')

    def test_vector_ops_Sub_1(self):
        input_string = 'vSub([3], [1])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[2]')

    def test_vector_ops_Sub_2(self):
        input_string = 'vSub([3, 4], [1, 6])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[2, -2]')

    def test_vector_ops_Sub_3(self):
        input_string = 'vSub([[3]], [[1]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[2]]')

    def test_vector_ops_Sub_4(self):
        input_string = 'vSub([[3, 2]], [[1, 5]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[2, -3]]')

    def test_vector_ops_Sub_5(self):
        input_string = 'vSub([[3, 5], [1, 6], [3, 7]], [[3, 5], [1, 6], [3, 7]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[0, 0], [0, 0], [0, 0]]')

    def test_vector_ops_MulNum_1(self):
        input_string = 'vMulNum(3, [1])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[3]')

    def test_vector_ops_MulNum_2(self):
        input_string = 'vMulNum([3, 4], -2)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[-6, -8]')

    def test_vector_ops_MulNum_3(self):
        input_string = 'vMulNum(1, [[3], [1]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[3], [1]]')

    def test_vector_ops_MulNum_4(self):
        input_string = 'vMulNum(-2, [[3, 2], [1, 5]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[-6, -4], [-2, -10]]')

    def test_vector_ops_MulNum_5(self):
        input_string = 'vMulNum([1], [[3, 2], [1, 5]])'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            tree.tree_calculate()

    def test_vector_ops_DP_1(self):
        input_string = 'vDP([3], [1])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '3')

    def test_vector_ops_DP_2(self):
        input_string = 'vDP([3, 4], [1, 6])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '27')

    def test_vector_ops_DP_3(self):
        input_string = 'vDP([3, 4], [1, 6])-27'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '0')

    def test_vector_ops_DP_4(self):
        input_string = 'vDP([3, 4], [1, 6])/10'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '2.7')

    def test_vector_ops_DP_5(self):
        input_string = 'vDP([1], [[3, 2], [1, 5]])'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            tree.tree_calculate()

    def test_vector_ops_DP_6(self):
        input_string = 'vDP([1], [3, 2])'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            tree.tree_calculate()

    def test_vector_ops_Get_1(self):
        input_string = 'vGet([3], 1)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '3')

    def test_vector_ops_Get_2(self):
        input_string = 'vGet([3, 4], 2)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '4')

    def test_vector_ops_Get_3(self):
        input_string = 'vGet([[3], [4]], 1)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[3]')

    def test_vector_ops_Get_4(self):
        input_string = 'vGet([[3, 4], [1, 6]], 2)'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[1, 6]')

    def test_vector_ops_Get_5(self):
        input_string = 'vGet(1, [[3, 2], [1, 5]])'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            tree.tree_calculate()

    def test_vector_ops_Get_6(self):
        input_string = 'vGet([3, 2], 1.0)'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            tree.tree_calculate()

    def test_vector_ops_Get_7(self):
        input_string = 'vGet([3, 2], 3)'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            tree.tree_calculate()

    def test_vector_ops_USub_1(self):
        input_string = 'vUSub([[3], [4]])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[-3], [-4]]')

    def test_vector_ops_USub_2(self):
        input_string = 'vUSub([1])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[-1]')

    def test_vector_ops_USub_3(self):
        input_string = 'vUSub(1)'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            tree.tree_calculate()

if __name__ == '__main__':
    unittest.main()
