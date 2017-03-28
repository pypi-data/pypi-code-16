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
        self.assertEquals(output_string, '1')

    def test_empty_double_vector(self):
        input_string = '[[2], [1]]'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[2], [1]]')

    def test_vector1(self):
        input_string = '[x]'

        var_shape = {'x': ()}

        tree = Tree(expression=input_string, var_shapes=var_shape)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, 'x')

    def test_vector2(self):
        input_string = '[x, y]'

        var_shape = {'x': (), 'y': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[x, y]')

    def test_vector3(self):
        input_string = '[[1, x], [2, y]]'

        var_shape = {'x': (), 'y': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[1, x], [2, y]]')

    def test_vector_ops_Add_1(self):
        input_string = 'vAdd([3], [1])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_vector_ops_Add_2(self):
        input_string = 'vAdd([3, 4], [1, 6])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[4, 10]')

    def test_vector_ops_Add_3(self):
        input_string = 'vAdd([3], [1])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_vector_ops_Add_4(self):
        input_string = 'vAdd([3, 2], [1, 5])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[4, 7]')

    def test_vector_ops_Add_5(self):
        input_string = 'vAdd([[3, 5], [1, 6], [3, 7]], [[3, 5], [1, 6], [3, 7]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[6, 10], [2, 12], [6, 14]]')

    def test_vector_ops_Sub_1(self):
        input_string = 'vSub([3], [1])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_vector_ops_Sub_2(self):
        input_string = 'vSub([3, 4], [1, 6])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[2, -2]')

    def test_vector_ops_Sub_3(self):
        input_string = 'vSub([[3]], [1])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_vector_ops_Sub_4(self):
        input_string = 'vSub([3, 2], [1, 5])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[2, -3]')

    def test_vector_ops_Sub_5(self):
        input_string = 'vSub([[3, 5], [1, 6], [3, 7]], [[3, 5], [1, 6], [3, 7]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[0, 0], [0, 0], [0, 0]]')

    def test_vector_ops_MulNum_1(self):
        input_string = 'vMulNum(3, [1])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

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
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[3, 2], [1, 5]]')

    def test_vector_ops_DP_1(self):
        input_string = 'vDP([3], [1])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

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

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

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
        self.assertEquals(output_string, '3')

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

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_vector_ops_USub_3(self):
        input_string = 'vUSub(1)'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            
            tree.tree_calculate()

    def test_nested_ops1(self):
        input_string = 'vAdd(vAdd([1, 2], [3, 4]), vAdd([5, 6], [7, 8]))'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[16, 20]')

    def test_nested_ops2(self):
        input_string = 'vAdd(vAdd([1, 2], [3, 4]), vSub([5, 6], [7, 8]))'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[2, 4]')

    def test_nested_ops3(self):
        input_string = 'vAdd(vMulNum(2, [3, 4]), vSub([5, 6], [7, 8]))'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[4, 6]')

    def test_nested_ops4(self):
        input_string = 'vSub(vMulNum(2, [3, 4]), vSub([5, 6], [7, 8]))'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[8, 10]')

    def test_nested_ops5(self):
        input_string = 'vAdd(vGet([[1, 2], [3, 4]], 1), [1, 2])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[2, 4]')

    def test_nested_ops6(self):
        input_string = 'vGet([1, 2], 2)-2'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '0')

    def test_nested_ops7(self):
        input_string = 'vDP(vGet([[1, 2], [1, 2]], 2), vAdd([1, 2], [3, 4]))'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '16')

    def test_nested_ops8(self):
        input_string = 'vUSub(vMulNum(-1, [1, 2]))'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[1, 2]')

    def test_nested_ops9(self):
        input_string = 'vAdd(vGet([[3], [1]], 1), [-3])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_nested_ops10(self):
        input_string = 'vAdd([1, 2], vAdd([1, 2, 3], [4, 5, 6]))'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            
            tree.tree_calculate()

    def test_nested_ops11(self):
        input_string = 'vAdd([1], [[1]])'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            
            tree.tree_calculate()

    def test_nested_ops12(self):
        input_string = 'vAdd(vDP([3], [4]), [5])'
        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)
            
            tree.tree_calculate()

    def test_nested_ops13(self):
        input_string = 'vMulNum([3], [1, 2])'
        tree = Tree(expression=input_string)
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[3, 6]')

    def test_transpose1(self):
        input_string = 'vT([1])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_transpose2(self):
        input_string = 'vT([1, 2])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[1], [2]]')

    def test_transpose3(self):
        input_string = 'vT([[1], [2]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[1, 2]')

    def test_transpose4(self):
        input_string = 'vT([[1, 2], [3, 4]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[1, 3], [2, 4]]')

    def test_transpose5(self):
        input_string = 'vAdd(vT([[1, 2, 3], [3, 4, 5]]), [[1, 3], [2, 4], [3, 5]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[2, 6], [4, 8], [6, 10]]')

    def test_mult1(self):
        input_string = 'vMul([1], [[2]])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_mult2(self):
        input_string = 'vMul([1], [2])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_mult3(self):
        input_string = 'vMul([1, 2], [[2], [0]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '2')

    def test_mult4(self):
        input_string = 'vMul([[1], [2]], [[2]])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_mult5(self):
        input_string = 'vMul([[1, 2], [3, 4]], [[2], [2]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[6], [14]]')

    def test_mult6(self):
        input_string = 'vMul([[1, 2], [3, 4]], [[2, 1], [2, 0]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[6, 1], [14, 3]]')

    def test_mult7(self):
        input_string = 'vMul([[1, 2], [3, 4]], [[2, 1, 3], [2, 4, 5]])'
        tree = Tree(expression=input_string)
        
        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[6, 9, 13], [14, 19, 29]]')

    def test_tens_mult1(self):
        input_string = 'vTMul([1], [[2]])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_tens_mult2(self):
        input_string = 'vTMul([1], [2])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_tens_mult3(self):
        input_string = 'vTMul([1, 2], [[2], [0]])'
        tree = Tree(expression=input_string)

        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[2, 4], [0, 0]]')

    def test_tens_mult4(self):
        input_string = 'vTMul([[1], [2]], [[2]])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_tens_mult5(self):
        input_string = 'vTMul([[1, 2], [3, 4]], [[2], [2]])'
        tree = Tree(expression=input_string)

        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[2, 4], [2, 4], [6, 8], [6, 8]]')

    def test_tens_mult6(self):
        input_string = 'vTMul([[1, 2], [3, 4]], [[2, 1], [2, 0]])'
        tree = Tree(expression=input_string)

        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[2, 1, 4, 2], [2, 0, 4, 0], [6, 3, 8, 4], [6, 0, 8, 0]]')

    def test_tens_mult7(self):
        input_string = 'vTMul([1, 2], [3, 4])'
        tree = Tree(expression=input_string)

        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[3, 4, 6, 8]')

    def test_tens_mult8(self):
        input_string = 'vTMul([[1], [2]], [[3], [4]])'
        tree = Tree(expression=input_string)

        tree.tree_calculate()
        output_string = tree.to_expression()
        self.assertEquals(output_string, '[[3], [4], [6], [8]]')

if __name__ == '__main__':
    unittest.main()
