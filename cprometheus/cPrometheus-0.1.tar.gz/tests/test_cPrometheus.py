import unittest
from cPrometheus import _AtomicValue


class TestCPrometheus(unittest.TestCase):
    def test_cPrometheus(self):
        instance = _AtomicValue()
        self.assertEqual(0.0, instance.get())
        instance.set(1.0)
        self.assertEqual(1.0, instance.get())
        instance.inc(2.0)
        self.assertEqual(3.0, instance.get())
