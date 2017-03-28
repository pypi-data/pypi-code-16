import unittest

from sqc.src.Tree import Tree


class Test(unittest.TestCase):
    def test_binary_op_sum(self):
        input_string = '1+1'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_binary_op_sub(self):
        input_string = '1-1'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_binary_op_mul(self):
        input_string = '1*1'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_binary_op_div(self):
        input_string = '1/1'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_binary_op_pow(self):
        input_string = '1**1'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_two_ops(self):
        input_string = '1+1+1'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_two_ops2(self):
        input_string = '1+1-1'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_three_ops(self):
        input_string = '1/1*1-1'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_order_ops1(self):
        input_string = '1*2/8*4'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_order_ops2(self):
        input_string = '1+2*3/4-5'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_order_pow(self):
        input_string = '1**2*3'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_parentheses(self):
        input_string = '(1+1)*(2+2)/(3-4)+(5*6)'
        tree = Tree(expression=input_string)
        
        self.assertEquals(tree.root.value.shape, ())

    def test_with_args1(self):
        input_string = '2+3+x'

        var_shape = {'x': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args2(self):
        input_string = 't-(3+x)'

        var_shape = {'x': (), 't': ()}

        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args3(self):
        input_string = '-(1+a)'

        var_shape = {'a': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args4(self):
        input_string = '(2+3+a)*(1+a)'

        var_shape = {'a': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args5(self):
        input_string = '1/(3*4+b+c)'

        var_shape = {'a': (), 'b': (), 'c': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args7(self):
        input_string = '+(1+3+x)'

        var_shape = {'x': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args8(self):
        input_string = '2*(x)'

        var_shape = {'x': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args9(self):
        input_string = '(3*x)/3'

        var_shape = {'x': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args10(self):
        input_string = '(x+1)*(1-2)'

        var_shape = {'x': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_with_args11(self):
        input_string = '((a+1)*c+b*a+b)/(b+c)'

        var_shape = {'a': (), 'b': (), 'c': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_uni_vector(self):
        input_string = '[1]'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, ())

    def test_uni_vector2(self):
        input_string = '[[1]]'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, ())

    def test_empty_double_vector(self):
        input_string = '[[2], [1]]'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (2, 1))

    def test_vector1(self):
        input_string = '[x]'

        var_shape = {'x': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, ())

    def test_vector1_1(self):
        input_string = '[x]'

        var_shape = {'x': (1, 1)}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, (1, 1))

    def test_vector2(self):
        input_string = '[x, y]'

        var_shape = {'x': (), 'y': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, (1, 2))

    def test_vector2_1(self):
        input_string = '[x, y]'

        var_shape = {'x': (1, 3), 'y': (1, 3)}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, (2, 3))

    def test_vector3(self):
        input_string = '[[1, x], [2, y]]'

        var_shape = {'x': (), 'y': ()}
        tree = Tree(expression=input_string, var_shapes=var_shape)

        self.assertEquals(tree.root.value.shape, (2, 2))

    def test_vector_ops_Add_2(self):
        input_string = 'vAdd([3, 4], [1, 6])'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (1, 2))

    def test_vector_ops_Add_4(self):
        input_string = 'vAdd([[3, 2]], [[1, 5]])'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (1, 2))

    def test_vector_ops_Add_5(self):
        input_string = 'vAdd([[3, 5], [1, 6], [3, 7]], [[3, 5], [1, 6], [3, 7]])'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (3, 2))

    def test_vector_ops_MulNum_2(self):
        input_string = 'vMulNum([3, 4], -2)'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (1, 2))

    def test_vector_ops_MulNum_3(self):
        input_string = 'vMulNum(1, [[3], [1]])'
        tree = Tree(expression=input_string)
        self.assertEquals(tree.root.value.shape, (2, 1))

    def test_vector_ops_MulNum_4(self):
        input_string = 'vMulNum(-2, [[3, 2], [1, 5]])'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (2, 2))

    def test_vector_ops_DP_1(self):
        input_string = 'vDP([3], [1])'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_vector_ops_DP_2(self):
        input_string = 'vDP([3, 4], [1, 6])'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, ())

    def test_vector_ops_DP_3(self):
        input_string = 'vDP([3, 4], [1, 6])-27'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, ())

    def test_vector_ops_DP_4(self):
        input_string = 'vDP([3, 4], [1, 6])/10'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, ())

    def test_vector_ops_Get_1(self):
        input_string = 'vGet([3], 1)'

        with self.assertRaises(Exception):
            tree = Tree(expression=input_string)

    def test_vector_ops_Get_2(self):
        input_string = 'vGet([3, 4], 2)'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, ())

    def test_vector_ops_Get_3(self):
        input_string = 'vGet([[3], [4]], 1)'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (1, 1))

    def test_vector_ops_Get_4(self):
        input_string = 'vGet([[3, 4], [1, 6]], 2)'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (1, 2))

    def test_vector_ops_USub_1(self):
        input_string = 'vUSub([[3], [4]])'
        tree = Tree(expression=input_string)

        self.assertEquals(tree.root.value.shape, (2, 1))

    def test_with_args1_err(self):
        input_string = '2+3+x'

        with self.assertRaises(Exception):
            var_shape = {'x': (1, 1)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_with_args2_err(self):
        input_string = 't-(3+x)'
        
        with self.assertRaises(Exception):
            var_shape = {'x': (2, 2), 't': (2, 2)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_with_args3_err(self):
        input_string = '-(1+a)'
        
        with self.assertRaises(Exception):
            var_shape = {'a': (1, 2)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_with_args5_err(self):
        input_string = '1/(3*4+b+c)'
        
        with self.assertRaises(Exception):
            var_shape = {'a': (), 'b': (), 'c': (1, 1)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_with_args7_err(self):
        input_string = '+(1+3+x)'
        
        with self.assertRaises(Exception):
            var_shape = {'x': (2,)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_with_args8_err(self):
        input_string = '2*(x)'
        
        with self.assertRaises(Exception):
            var_shape = {'x': (1, 1)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_with_args9_err(self):
        input_string = '(3*x)/3'
        
        with self.assertRaises(Exception):
            var_shape = {'x': (1, 3)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_with_args10_err(self):
        input_string = '(x+1)*(1-2)'
        
        with self.assertRaises(Exception):
            var_shape = {'x': (1, 1)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_with_args11_err(self):
        input_string = '((a+1)*c+b*a+b)/(b+c)'
        
        with self.assertRaises(Exception):
            var_shape = {'a': (), 'b': (), 'c': (1, 2)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_vector2_err(self):
        input_string = '[x, y]'
        
        with self.assertRaises(Exception):
            var_shape = {'x': (1, 1), 'y': (1, 2)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_vector2_1_err(self):
        input_string = '[x, y]'
        
        with self.assertRaises(Exception):
            var_shape = {'x': (1, 3), 'y': (3, 3)}
            tree = Tree(expression=input_string, var_shapes=var_shape)

    def test_vector3_err(self):
        input_string = '[[1, x], [2, y]]'
        
        with self.assertRaises(Exception):
            var_shape = {'x': (1, 1), 'y': (1, 2)}
            tree = Tree(expression=input_string, var_shapes=var_shape)
            

if __name__ == '__main__':
    unittest.main()
