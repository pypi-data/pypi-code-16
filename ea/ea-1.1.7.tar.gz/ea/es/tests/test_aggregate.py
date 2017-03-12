import unittest

from ea.es.tests.aggregate import TestAggegrate


class AggregateTestCase(unittest.TestCase):

    def test_invoked_method_sets_attribute(self):
        agg = TestAggegrate()
        agg.foo(1)
        self.assertEqual(agg.arg, 1)

    def test_invoked_method_publishes_event(self):
        agg = TestAggegrate()
        agg.foo(1)
        self.assertEqual(len(list(agg.events)), 1)

    def test_invoked_method_increases_version(self):
        agg = TestAggegrate()
        version = agg.events.version
        agg.foo(1)
        self.assertEqual(agg.events.version, version + 1)

    def test_publisher_is_unique(self): 
        agg1 = TestAggegrate()
        agg2 = TestAggegrate()
        self.assertNotEqual(agg1.events, agg2.events)
