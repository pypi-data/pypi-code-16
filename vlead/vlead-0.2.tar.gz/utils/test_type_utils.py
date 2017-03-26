
# -*- coding: utf-8 -*-
import unittest
from unittest import TestCase
from type_utils import *
import types


class TestIsInstance(TestCase):
    TESTING = True

    def test_is_int(self):
        print "test_instances"
        self.assertEqual(is_int(10), True)
        self.assertEqual(is_int(10.0), False)
        self.assertEqual(is_bool(False), True)
        self.assertEqual(is_bool(10), False)
        self.assertEqual(is_str('hello world'), True)
        self.assertEqual(is_str(False), False)
        self.assertEqual(is_str_or_none(None), True)
        self.assertEqual(is_dict({'email': 'xyz@g.com'}), True)
        self.assertEqual(is_dict("{'email': 'xyz@g.com'}"), False)

def rem(a, b):
    return a % b

check_even = check_pred(lambda a: isinstance(a,int) & rem(a,2) == 0)

class TestCheckPred(TestCase):
    TESTING = True
    '''test_check_pred'''

    def test_check_even(self):
        print "test_check_pred"
        self.assertEqual(check_even(4), 4)
        self.assertRaises(TypeError, check_even, 5)
        self.assertEqual(check_even(False), False)  # False == 0 in Python

class TestCheckAlphabeticStr(TestCase):
    TESTING = True
    """Tests for  alphabetic strings"""
    def test_check_alphabetic_str(self):
        print "test_check_alphabetic_str"
        self.assertEqual(check_alphabetic_str("Hello"), "Hello")
        self.assertEqual(check_alphabetic_str("M. N. Ray"), "M. N. Ray")
        self.assertRaises(TypeError, check_alphabetic_str, "123hello")


class TestCheckString(TestCase):
    TESTING = True
    """Tests for strings"""
    def test_check_string(self):
        print "test_check_string"
        self.assertEqual(check_string("Hello"), "Hello")
        self.assertEqual(check_string("M. N. Ray"), "M. N. Ray")
        self.assertRaises(TypeError, check_alphabetic_str, 123)


class TestCheckDate(TestCase):
    TESTING = True
    """Tests for date"""
    def test_check_date(self):
        print "test_check_date"
        self.assertEqual(check_date(datetime.datetime.strptime("30-06-2016", "%d-%m-%Y").date()), datetime.datetime.strptime("30-06-2016", "%d-%m-%Y").date())
        self.assertEqual(check_date(datetime.datetime.strptime("29-06-2016", "%d-%m-%Y").date()), datetime.datetime.strptime("29-06-2016", "%d-%m-%Y").date())
        self.assertRaises(TypeError, check_date, 123)


class TestCheckInt(TestCase):
    TESTING = True
    """Tests for integer"""
    def test_check_integer(self):
        print "test_check_integer"
        self.assertEqual(check_int(123), 123)
        self.assertRaises(TypeError, check_int, "abc")

    def test_more_alphabetic_strings(self):
        print "test_more_alphabetic_strings"
        # this looks wierd!  Should it be a name?
        self.assertEqual(check_alphabetic_str(".  ."), ".  .")


class TestCheckEmailStr(TestCase):
    TESTING = True
    """Tests for Email strings"""
    def test_check_email_str(self):
        print "test_check_email_str"
        self.assertEqual(check_email_str("web@gnu.org"), "web@gnu.org")
        self.assertRaises(TypeError, check_email_str, "@gnu.org")

class TestCheckInstance(TestCase):
    TESTING = True
    """Tests for Check instances"""

    def test_check_inst(self):
        print "test_check_instance"
        self.assertEqual(check_int(3), 3)
        self.assertEqual(check_str("abc"), "abc")

        self.assertEqual(isinstance(
                         check_dict({'x': 3, 'y': 5}),
                         dict),
                         True)
        self.assertEqual(isinstance(
                         check_function(check_function),
                         types.FunctionType),
                         True)

        self.assertRaises(TypeError, check_pos_int, 0)
        self.assertRaises(TypeError, check_non_neg_int, -1)
if __name__ == '__main__':
    unittest.main()
