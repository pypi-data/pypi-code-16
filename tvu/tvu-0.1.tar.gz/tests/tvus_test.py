# coding: utf-8
from test_utils import TestCase
from test_compat import text

import tvu
import tvu.tvus as tvus


class BoundedIntTest(TestCase):

    def unbounded_int_test(self):
        @tvu(x=tvus.bounded_int())
        def foo(x):
            return x

        self.assertEqual(foo(100), 100)
        self.assertEqual(foo(-100), -100)
        self.assertEqual(foo(1.), 1)
        self.assertTrue(isinstance(foo(1.), int))
        self.assertEqual(foo(-1.), -1)
        self.assertTrue(isinstance(foo(-1.), int))
        with self.assertRaises(TypeError, 'x must be int or float, not None'):
            foo(None)

        with self.assertRaises(ValueError,
                               'x must be a round number, not: 0.5'):
            foo(.5)

    def lower_bound_int_test(self):
        @tvu(x=tvus.bounded_int(minimum=0))
        def foo(x):
            return x

        self.assertEqual(foo(100), 100)
        self.assertEqual(foo(0), 0)
        self.assertEqual(foo(1.), 1)
        self.assertTrue(isinstance(foo(1.), int))
        with self.assertRaises(TypeError, 'x must be int or float, not None'):
            foo(None)

        with self.assertRaises(ValueError,
                               'x must be a round number, not: 0.5'):
            foo(.5)

        err_msg = 'x must be an integer greater or equal to 0, not: -1'
        with self.assertRaises(ValueError, err_msg):
            foo(-1)
        err_msg = 'x must be an integer greater or equal to 0, not: -1.0'
        with self.assertRaises(ValueError, err_msg):
            foo(-1.)

    def upper_bound_int_test(self):
        @tvu(x=tvus.bounded_int(maximum=0))
        def foo(x):
            return x

        self.assertEqual(foo(-100), -100)
        self.assertEqual(foo(0), 0)
        self.assertEqual(foo(-1.), -1)
        self.assertTrue(isinstance(foo(-1.), int))
        with self.assertRaises(TypeError, 'x must be int or float, not None'):
            foo(None)

        with self.assertRaises(ValueError,
                               'x must be a round number, not: 0.5'):
            foo(.5)

        err_msg = 'x must be an integer lesser or equal to 0, not: 1'
        with self.assertRaises(ValueError, err_msg):
            foo(1)
        err_msg = 'x must be an integer lesser or equal to 0, not: 1.0'
        with self.assertRaises(ValueError, err_msg):
            foo(1.)

    def bound_int_test(self):
        @tvu(x=tvus.bounded_int(minimum=0, maximum=10))
        def foo(x):
            return x

        self.assertEqual(foo(0), 0)
        self.assertEqual(foo(10), 10)
        self.assertEqual(foo(1.), 1)
        self.assertTrue(isinstance(foo(1.), int))
        with self.assertRaises(TypeError, 'x must be int or float, not None'):
            foo(None)

        with self.assertRaises(ValueError,
                               'x must be a round number, not: 0.5'):
            foo(.5)

        err_msg = 'x must be an integer between 0 and 10 (inclusive), not: 11'
        with self.assertRaises(ValueError, err_msg):
            foo(11)
        err_msg = \
            'x must be an integer between 0 and 10 (inclusive), not: -1.0'
        with self.assertRaises(ValueError, err_msg):
            foo(-1.)

    def positive_int_test(self):
        @tvu(x=tvus.PositiveInt)
        def foo(x):
            return x

        self.assertEqual(foo(100), 100)
        self.assertEqual(foo(1.), 1)
        self.assertTrue(isinstance(foo(1.), int))
        with self.assertRaises(TypeError, 'x must be int or float, not None'):
            foo(None)

        with self.assertRaises(ValueError,
                               'x must be a round number, not: 0.5'):
            foo(.5)

        err_msg = 'x must be an integer greater or equal to 1, not: -1'
        with self.assertRaises(ValueError, err_msg):
            foo(-1)
        err_msg = 'x must be an integer greater or equal to 1, not: 0.0'
        with self.assertRaises(ValueError, err_msg):
            foo(0.)


class IterableTest(TestCase):

    def iterable_test(self):
        @tvu(x=tvus.Iterable)
        def foo(x):
            pass

        foo([])
        foo(iter({1, 2, 3}))
        with self.assertRaises(TypeError, 'x must be iterable, not None'):
            foo(None)

    def not_stealing_test(self):
        @tvu(x=tvus.Iterable)
        def foo(x):
            return next(iter(x))

        self.assertEqual(foo([1, 2]), 1)

        def bar():
            yield 1
            yield 2

        self.assertEqual(foo(bar()), 1)


class TextTest(TestCase):

    def text_test(self):
        @tvu(x=tvus.Text)
        def foo(x):
            return x

        self.assertEqual(foo(b''), u'')
        self.assertTrue(isinstance(foo(b''), text))
        self.assertEqual(foo(u''), u'')
        self.assertTrue(isinstance(foo(u''), text))
        self.assertEqual(foo(b'foo'), u'foo')
        self.assertTrue(isinstance(foo(b'foo'), text))
        self.assertEqual(foo(u'bar'), u'bar')
        self.assertTrue(isinstance(foo(u'bar'), text))

        err_msg = 'x must be %s or %s, not None' % (text.__name__,
                                                    bytes.__name__)
        with self.assertRaises(TypeError, err_msg):
            foo(None)

        err_msg = 'x must be unicode text, or ascii-only bytestring'
        with self.assertRaises(ValueError, err_msg):
            foo((u'żółw').encode('utf-8'))


class NonEmptyTextTest(TestCase):

    def non_empty_text_test(self):
        @tvu(x=tvus.NonEmptyText)
        def foo(x):
            return x

        self.assertEqual(foo(b'foo'), u'foo')
        self.assertTrue(isinstance(foo(b'foo'), type(u'')))  # compat
        self.assertEqual(foo(u'bar'), u'bar')
        self.assertTrue(isinstance(foo(u'bar'), type(u'')))  # compat

        err_msg = 'x must be %s or %s, not None' % (text.__name__,
                                                    bytes.__name__)
        with self.assertRaises(TypeError, err_msg):
            foo(None)

        err_msg = 'x must be unicode text, or ascii-only bytestring'
        with self.assertRaises(ValueError, err_msg):
            foo((u'żółw').encode('utf-8'))

        with self.assertRaises(ValueError, 'x must be non-empty string'):
            foo(b'')

        with self.assertRaises(ValueError, 'x must be non-empty string'):
            foo(u'')
