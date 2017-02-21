
import unittest
from stateutil import incrementor

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


class TestIncrementor(unittest.TestCase):

    def setUp(self):
        self.start_value = 10
        self.incr = incrementor.Incrementor(start_value=self.start_value)

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(self.incr.current, self.start_value)
        self.assertEqual(self.incr.max, self.start_value)

    def test_prev(self):
        self.assertEqual(self.incr.prev(), self.start_value - 1)
        self.assertEqual(self.incr.prev(), self.start_value - 2)
        self.assertEqual(self.incr.max, self.start_value)

    def test_previous(self):
        self.assertEqual(self.incr.previous(), self.start_value - 1)
        self.assertEqual(self.incr.previous(), self.start_value - 2)
        self.assertEqual(self.incr.max, self.start_value)

    def test_next(self):
        self.assertEqual(self.incr.next(), self.start_value + 1)
        self.assertEqual(self.incr.max, self.start_value + 1)
        self.assertEqual(self.incr.next(), self.start_value + 2)
        self.assertEqual(self.incr.max, self.start_value + 2)

    def test_max(self):
        self.assertEqual(self.incr.max, self.start_value)
        _ = self.incr.prev()
        self.assertEqual(self.incr.max, self.start_value)
        _ = self.incr.next()
        _ = self.incr.next()
        self.assertEqual(self.incr.max, self.start_value + 1)

    def test_set(self):
        self.assertEqual(self.incr.current, self.start_value)
        self.incr.set(value=15)
        self.assertEqual(self.incr.max, 15)
        self.assertEqual(self.incr.current, 15)

    def test_start(self):
        self.assertEqual(self.incr.start(), self.start_value)
        self.assertEqual(self.incr.current, self.start_value)
        self.assertEqual(self.incr.max, self.start_value)


if __name__ == u'__main__':
    unittest.main()
