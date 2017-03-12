import unittest
import uuid

from ea.lib.datastructures import DTO
from ea.exc import ImplementationError
from ea.es.tests.aggregate import TestAggegrate
from ea.es.exc import InconsistentAggregateState


class PublisherTestCase(unittest.TestCase):

    def setUp(self):
        self.agg = TestAggegrate()
        self.agg.id = str(uuid.uuid4())
        self.publisher = self.agg.events

    def test_can_not_publish_during_stream(self):
        with self.assertRaises(ImplementationError):
            with self.publisher.stream():
                self.agg.foo(1)

    def test_can_not_handle_inconsistent_event(self):
        e = DTO(version=-1)
        with self.assertRaises(InconsistentAggregateState):
            self.publisher.handle(e)

    def test_consume_sets_cid(self):
        self.agg.foo(0)
        self.assertEqual(self.publisher.count(), 1)
        for x in self.publisher.consume():
            self.assertTrue(hasattr(x, 'cid'))

    def test_consume_empties_publisher(self):
        self.assertEqual(self.publisher.count(), 0)
        self.agg.foo(0)
        self.assertEqual(self.publisher.count(), 1)
        for x in self.publisher.consume():
            pass
        self.assertEqual(self.publisher.count(), 0)

    def test_event_increases_count(self):
        self.assertEqual(self.publisher.count(), 0)
        self.agg.foo(0)
        self.assertEqual(self.publisher.count(), 1)

    def test_missing_handler_raises_implementationerror(self):
        with self.assertRaises(ImplementationError):
            self.agg.missing()
