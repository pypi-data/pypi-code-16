import unittest
from lazyprop import lazyprop


class TestLazyProp(unittest.TestCase):
    def test_lazyprop(self):
        class Foo(object):
            def __init__(self):
                self.load_count = 0

            @lazyprop
            def lazy(self):
                self.load_count += 1
                return 1

        f = Foo()
        self.assertEqual(f.lazy, 1)
        self.assertEqual(f.load_count, 1)
        should_by_cached = f.lazy;
        self.assertEqual(f.load_count, 1)
