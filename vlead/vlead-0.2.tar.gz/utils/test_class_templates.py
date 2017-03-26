
# -*- coding: utf-8 -*-
import unittest
from unittest import TestCase
from datetime import datetime
from type_utils import *
from class_templates import *
class TestMeta(TestCase):
    def test_meta(self):
        Bar = meta("Bar")
        bar = Bar()
        self.assertTrue(isinstance(bar, Bar))
class TestValueClassTemplate(TestCase):

    Name = ValueClassTemplate.mk_class("Name", is_alphabetic_str)
    Name.n1 = Name("ravi")
    Name.n2 = Name("Ravi")

        
    def test_value_class_template(self):
        Name = TestValueClassTemplate.Name
        print "test_value_class_template"
        self.assertEqual(Name.n1.get(), "ravi", "n1.get()")
        Name.n1.set("Ravi")
        self.assertTrue(Name.n1.get()==Name.n2.get(), "n1.get()==n2.get()")
class TestClassTemplate(TestCase):
    Foo = ClassTemplate.mk_class("Foo",  x=is_int, y=is_str)
    Foo.foo = Foo(x=4, y="hello")

    def test_class_template_with_Foo(self):
        print "test_class_template_with_Foo"
        Foo = TestClassTemplate.Foo

        self.assertEqual(Foo.foo.get("x"), 4, "foo.get(x)==4")
        self.assertEqual(Foo.foo.get("y"), "hello", "foo.get(y)==hello")

        Foo.foo.set(x=7)
        self.assertEqual(Foo.foo.get("x"), 7, "foo.get(x)==7")
        self.assertTrue(Foo.foo.inv({'x': Foo.foo.get("x")}), "Foo.foo.inv")

    def temp_inv(obj, args):
        return args["min"] <= args["max"]

    Temp = ClassTemplate.mk_class("Temp", min=is_int, max=is_int, inv=temp_inv)

    Temp.temp = Temp(min=4, max=5)

    def eq_fn(self, other):
        return \
            isinstance(other, self.__class__) and \
            self.get("min") == other.get("min") and \
            self.get("max") == other.get("max")

    Temp.__eq__ = eq_fn

    def test_class_template_with_Temp(self):
        print "test_class_template_with_Temp"
        Temp = TestClassTemplate.Temp
        self.assertEqual(Temp.temp.get("min"), 4, "temp.get(min)==4")
        self.assertEqual(Temp.temp.get("max"), 5, "temp.get(max)==5")

        Temp.temp.set(min=0)
        self.assertEqual(Temp.temp.get("min"), 0, "temp.get(min)==0")
        self.assertRaises(TypeError, lambda: Temp.temp.set(min=9),
                          "temp.set(min=9) Error")

        temp2 = Temp(min=0, max=5)

        self.assertTrue(Temp.temp == temp2, "temp==temp2")

    def test_class_template_with_many_objects(self):
        print "test_class_template_with_many_objects"
        Name = ClassTemplate.mk_class("Name", name=is_alphabetic_str)
        name = Name(name="Jimi Hendrix")
        Email = ClassTemplate.mk_class("Email", email=is_email_str)
        email = Email(email="jimi@gnu.org")
        User = ClassTemplate.mk_class("User",
                                       name=is_inst(Name),
                                       email=is_inst(Email))
        usr = User(name=name, email=email)
        self.assertEqual(usr.get('name').get('name'), 'Jimi Hendrix')
        self.assertEqual(usr.get('email').get('email'), 'jimi@gnu.org')
        self.assertEqual(usr.to_client()['email']['email'], 'jimi@gnu.org')

if __name__ == '__main__':
    unittest.main()
