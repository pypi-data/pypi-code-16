# test_stack.py
# Author: Sébastien Combéfis
# Version: March 24, 2017

import unittest

import stack

class TestArrayStack(unittest.TestCase):
    def setUp(self):
        self.__s = stack.ArrayStack(5)

    def test_size(self):
        s = self.__s
        self.assertEqual(s.size(), 0)
        s.push(1)
        s.push(2)
        self.assertEqual(s.size(), 2)
        s.top()
        self.assertEqual(s.size(), 2)
        s.pop()
        self.assertEqual(s.size(), 1)

    def test_isempty(self):
        s = self.__s
        self.assertTrue(s.isempty())
        s.push(1)
        s.push(2)
        self.assertFalse(s.isempty())
        s.top()
        self.assertFalse(s.isempty())
        s.pop()
        s.pop()
        self.assertTrue(s.isempty())

    def test_top(self):
        s = self.__s
        with self.assertRaises(stack.EmptyStackError):
            s.top()
        s.push(1)
        s.push(2)
        self.assertEquals(s.top(), 2)
        s.pop()
        self.assertEquals(s.top(), 1)

    def test_pop(self):
        s = self.__s
        with self.assertRaises(stack.EmptyStackError):
            s.pop()
        s.push(1)
        s.push(2)
        self.assertEquals(s.pop(), 2)
        self.assertEquals(s.pop(), 1)

    def test_push(self):
        s = self.__s
        s.push(1)
        s.push(2)
        self.assertEquals(s.top(), 2)
        self.assertEquals(s.size(), 2)
        s.push(3)
        s.push(4)
        s.push(5)
        self.assertEquals(s.top(), 5)
        self.assertEquals(s.size(), 5)
        with self.assertRaises(stack.FullStackError):
            s.push(6)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestArrayStack)
    runner = unittest.TextTestRunner()
    exit(not runner.run(suite).wasSuccessful())
