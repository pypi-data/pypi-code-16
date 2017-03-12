import unittest
import uuid

from ea.es.tests.aggregate import TestAggegrate
from ea.es.tests.aggregate import TestRepository


class RepositoryTestCase(unittest.TestCase):

    def setUp(self):
        self.agg = TestAggegrate()
        self.events = self.agg.events
        self.repo = TestRepository()
        self.repo.persist(self.agg)
        self.agg.foo(1)

    def test_repo_clears_events(self):
        self.assertTrue(self.agg.id is not None)
        self.repo.persist(self.agg)
        self.assertEqual(self.events.count(),0)
