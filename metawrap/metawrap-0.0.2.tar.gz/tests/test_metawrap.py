#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_metawrap
----------------------------------

Tests for `metawrap` module.
"""

from __future__ import print_function


__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Mar 25, 2015 13:30:52 EDT$"


import functools
import sys
import unittest

from metawrap import metawrap


class TestWrappers(unittest.TestCase):
    def setUp(self):
        def setup_with_setup_state_2(a_callable):
            print("setup_2")
            self.assertFalse(hasattr(a_callable, "a"))

        self.setup_with_setup_state_2 = setup_with_setup_state_2

        def setup_with_setup_state_1(a_callable):
            print("setup_1")
            setattr(a_callable, "a", 5)

        self.setup_with_setup_state_1 = setup_with_setup_state_1

        def teardown_with_setup_state_1(a_callable):
            print("teardown_1")
            delattr(a_callable, "a")

        self.teardown_with_setup_state_1 = teardown_with_setup_state_1

        def teardown_with_setup_state_2(a_callable):
            print("teardown_2")
            self.assertFalse(hasattr(a_callable, "a"))

        self.teardown_with_setup_state_2 = teardown_with_setup_state_2


    def tearDown(self):
        del self.setup_with_setup_state_2
        del self.setup_with_setup_state_1
        del self.teardown_with_setup_state_1
        del self.teardown_with_setup_state_2


    def test_update_wrapper(self):
        def wrapper(a_callable):
            def wrapped(*args, **kwargs):
                return(a_callable(*args, **kwargs))

            return(wrapped)

        def func(a, b=2):
            return(a + b)

        func_wrapped_1 = functools.update_wrapper(wrapper, func)
        if not hasattr(func_wrapped_1, "__wrapped__"):
            setattr(func_wrapped_1, "__wrapped__", func)

        func_wrapped_2 = metawrap.update_wrapper(
            wrapper, func
        )

        self.assertEqual(func_wrapped_1, func_wrapped_2)


    def test_wraps(self):
        def wrapper(a_callable):
            def wrapped(*args, **kwargs):
                return(a_callable(*args, **kwargs))

            return(wrapped)

        def func(a, b=2):
            return(a + b)

        func_wrapped_1 = functools.wraps(wrapper)(func)
        if not hasattr(func_wrapped_1, "__wrapped__"):
            setattr(func_wrapped_1, "__wrapped__", func)

        func_wrapped_2 = metawrap.wraps(wrapper)(
            func
        )

        self.assertEqual(func_wrapped_1, func_wrapped_2)


    def test_identity_wrapper(self):
        def func(a, b=2):
            return(a + b)

        func_wrapped = metawrap.identity_wrapper(
            func
        )

        self.assertNotEqual(func_wrapped, func)
        self.assertFalse(hasattr(func, "__wrapped__"))
        self.assertTrue(hasattr(func_wrapped, "__wrapped__"))
        self.assertEqual(func_wrapped.__wrapped__, func)
        self.assertEqual(func_wrapped(0), func(0))


    def test_static_variables(self):
        def func(a, b=2):
            return(a + b)

        func_wrapped = metawrap.static_variables(
            c=7
        )(
            func
        )

        self.assertEqual(func_wrapped.__wrapped__, func)
        self.assertFalse(hasattr(func, "c"))
        self.assertTrue(hasattr(func_wrapped, "c"))
        self.assertEqual(func_wrapped.c, 7)


    def test_metaclass_0(self):
        class Meta(type):
            pass

        class Class(object):
            pass

        ClassWrapped = metawrap.metaclass(Meta)(Class)

        self.assertNotEqual(ClassWrapped, Class)
        self.assertFalse(hasattr(Class, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped, "__wrapped__"))
        self.assertEqual(ClassWrapped.__wrapped__, Class)

    def test_metaclass_1(self):
        class Meta(type):
            pass

        class Class(object):
            __slots__ = ("__special_object__",)

            def __init__(self):
                self.__special_object__ = object

        ClassWrapped = metawrap.metaclass(Meta)(Class)

        self.assertNotEqual(ClassWrapped, Class)
        self.assertFalse(hasattr(Class, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped, "__wrapped__"))
        self.assertEqual(ClassWrapped.__wrapped__, Class)

        a = Class()
        b = ClassWrapped()

        self.assertTrue(hasattr(a, "__special_object__"))
        self.assertTrue(hasattr(b, "__special_object__"))
        self.assertEqual(b.__special_object__, a.__special_object__)


    def test_metaclasses_0(self):
        class Meta1(type):
            pass

        class Meta2(type):
            pass

        class Class(object):
            pass

        ClassWrapped = metawrap.metaclasses(
            Meta1, Meta2
        )(Class)

        self.assertNotEqual(ClassWrapped, Class)
        self.assertFalse(hasattr(Class, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped.__wrapped__, "__wrapped__"))
        self.assertEqual(ClassWrapped.__wrapped__.__wrapped__, Class)


    def test_metaclasses_1(self):
        class Meta1(type):
            pass

        class Meta2(type):
            pass

        class Class(object):
            __slots__ = ("__special_object__",)

            def __init__(self):
                self.__special_object__ = object

        ClassWrapped = metawrap.metaclasses(
            Meta1, Meta2
        )(Class)

        self.assertNotEqual(ClassWrapped, Class)
        self.assertFalse(hasattr(Class, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped.__wrapped__, "__wrapped__"))
        self.assertEqual(ClassWrapped.__wrapped__.__wrapped__, Class)

        a = Class()
        b = ClassWrapped()

        self.assertTrue(hasattr(a, "__special_object__"))
        self.assertTrue(hasattr(b, "__special_object__"))
        self.assertEqual(b.__special_object__, a.__special_object__)


    def test_class_static_variables(self):
        class Class(object):
            pass

        ClassWrapped = metawrap.class_static_variables(a=5)(Class)

        self.assertNotEqual(ClassWrapped, Class)
        self.assertFalse(hasattr(Class, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped, "__wrapped__"))
        self.assertEqual(ClassWrapped.__wrapped__, Class)

        self.assertFalse(hasattr(Class, "a"))
        self.assertTrue(hasattr(ClassWrapped, "a"))
        self.assertEqual(ClassWrapped.a, 5)


    def test_class_decorate_all_methods(self):
        class Class(object):
            def __init__(self):
                pass

        ClassWrapped = metawrap.class_decorate_all_methods(
            metawrap.identity_wrapper
        )(Class)

        self.assertNotEqual(ClassWrapped, Class)
        self.assertFalse(hasattr(Class, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped, "__wrapped__"))
        self.assertEqual(ClassWrapped.__wrapped__, Class)

        self.assertNotEqual(ClassWrapped.__init__, Class.__init__)
        self.assertFalse(hasattr(Class.__init__, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped.__init__, "__wrapped__"))

        if sys.version_info.major < 3:
            self.assertNotEqual(
                ClassWrapped.__init__.__wrapped__,
                Class.__init__
            )
        else:
            self.assertEqual(ClassWrapped.__init__.__wrapped__, Class.__init__)

        self.assertEqual(ClassWrapped.__wrapped__.__init__, Class.__init__)


    def test_class_decorate_methods(self):
        class Class(object):
            def __init__(self):
                pass

            def func_0(self):
                pass

        ClassWrapped = metawrap.class_decorate_methods(
            func_0=metawrap.identity_wrapper
        )(Class)

        self.assertNotEqual(ClassWrapped, Class)
        self.assertFalse(hasattr(Class, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped, "__wrapped__"))
        self.assertEqual(ClassWrapped.__wrapped__, Class)

        self.assertEqual(ClassWrapped.__init__, Class.__init__)
        self.assertFalse(hasattr(Class.__init__, "__wrapped__"))
        self.assertFalse(hasattr(ClassWrapped.__init__, "__wrapped__"))
        self.assertEqual(ClassWrapped.__wrapped__.__init__, Class.__init__)

        self.assertNotEqual(ClassWrapped.func_0, Class.func_0)
        self.assertFalse(hasattr(Class.func_0, "__wrapped__"))
        self.assertTrue(hasattr(ClassWrapped.func_0, "__wrapped__"))

        if sys.version_info.major < 3:
            self.assertNotEqual(ClassWrapped.func_0.__wrapped__, Class.func_0)
        else:
            self.assertEqual(ClassWrapped.func_0.__wrapped__, Class.func_0)

        self.assertEqual(ClassWrapped.__wrapped__.func_0, Class.func_0)

    def test_unwrap(self):
        def func_0():
            pass

        func_1 = metawrap.identity_wrapper(func_0)
        func_2 = metawrap.identity_wrapper(func_1)

        self.assertEqual(metawrap.unwrap(func_1), func_0)
        self.assertNotEqual(metawrap.unwrap(func_2), func_1)
        self.assertEqual(metawrap.unwrap(func_2), func_0)

    def test_tied_call_args(self):
        def func_0(a, b=5, *v, **k):
            return(a + b + sum(v) + sum(list(k.values())))

        tied_args, args, kwargs = metawrap.tied_call_args(
            func_0, 1
        )
        self.assertEqual(list(tied_args.items()), [("a", 1), ("b", 5)])
        self.assertEqual(args, tuple())
        self.assertEqual(list(kwargs.items()), [])

        tied_args, args, kwargs = metawrap.tied_call_args(
            func_0, a=1, c=7
        )
        self.assertEqual(list(tied_args.items()), [("a", 1), ("b", 5)])
        self.assertEqual(args, tuple())
        self.assertEqual(list(kwargs.items()), [("c", 7)])

        tied_args, args, kwargs = metawrap.tied_call_args(
            func_0, 1, 2, 3, c=7
        )
        self.assertEqual(list(tied_args.items()), [("a", 1), ("b", 2)])
        self.assertEqual(args, (3,))
        self.assertEqual(list(kwargs.items()), [("c", 7)])

    def test_repack_call_args(self):
        def func_0(a, b=5, *v, **k):
            return(a + b + sum(v) + sum(list(k.values())))

        args, kwargs = metawrap.repack_call_args(func_0, 1)
        self.assertEqual(args, (1,))
        self.assertEqual(list(kwargs.items()), [("b", 5)])

        args, kwargs = metawrap.repack_call_args(
            func_0, a=1, c=7
        )
        self.assertEqual(args, tuple())
        self.assertEqual(sorted(kwargs.items()), [("a", 1), ("b", 5), ("c", 7)])

        args, kwargs = metawrap.repack_call_args(
            func_0, 1, 2, 3, c=7
        )
        self.assertEqual(args, (1, 2, 3))
        self.assertEqual(sorted(kwargs.items()), [("c", 7)])

    def test_with_setup_state_1a(self):
        @metawrap.with_setup_state_handler
        @metawrap.with_setup_state()
        def wrapped():
            print("test")

        wrapped()

    def test_with_setup_state_1b(self):
        @metawrap.with_setup_state(self.setup_with_setup_state_1,
                                   self.teardown_with_setup_state_1)
        def func():
            print("test")
            self.assertTrue(hasattr(func, "a"))
            self.assertEqual(getattr(func, "a"), 5)

        func2 = metawrap.with_setup_state_handler(func)

        func2()

    def test_with_setup_state_2a(self):
        @metawrap.with_setup_state(self.setup_with_setup_state_2,
                                   self.teardown_with_setup_state_2)
        @metawrap.with_setup_state(self.setup_with_setup_state_1,
                                   self.teardown_with_setup_state_1)
        def func():
            print("test")
            self.assertTrue(hasattr(func, "a"))
            self.assertEqual(getattr(func, "a"), 5)

        func2 = metawrap.with_setup_state_handler(func)

        func2()

    def test_with_setup_state_2b(self):
        @metawrap.with_setup_state()
        @metawrap.with_setup_state(self.setup_with_setup_state_2,
                                   self.teardown_with_setup_state_2)
        def func():
            print("test")
            self.assertFalse(hasattr(func, "a"))

        func2 = metawrap.with_setup_state_handler(func)

        func2()

    def test_with_setup_state_2c(self):
        @metawrap.with_setup_state(self.setup_with_setup_state_2,
                                   self.teardown_with_setup_state_2)
        @metawrap.with_setup_state()
        def func():
            print("test")
            self.assertFalse(hasattr(func, "a"))

        func2 = metawrap.with_setup_state_handler(func)

        func2()

    def test_with_setup_state_2d(self):
        @metawrap.with_setup_state()
        @metawrap.with_setup_state()
        def func():
            print("test")
            self.assertFalse(hasattr(func, "a"))

        func2 = metawrap.with_setup_state_handler(func)

        func2()


    def test_with_setup_state_6(self):
        @metawrap.with_setup_state()
        @metawrap.with_setup_state()
        @metawrap.with_setup_state()
        @metawrap.with_setup_state()
        @metawrap.with_setup_state()
        @metawrap.with_setup_state()
        def func():
            print("test")
            self.assertFalse(hasattr(func, "a"))

        func2 = metawrap.with_setup_state_handler(func)

        func2()


if __name__ == '__main__':
    sys.exit(unittest.main())
