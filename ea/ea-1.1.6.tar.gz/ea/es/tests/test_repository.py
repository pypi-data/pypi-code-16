import unittest

from ea.es.tests.aggregate import TestAggegrate
from ea.es.tests.aggregate import TestRepository


class RepositoryTestCase(unittest.TestCase):

    def setUp(self):
        self.agg = TestAggegrate()
        self.events = self.agg.events
        self.repo = TestRepository()
        self.agg.foo(1)

    def test_repo_clears_events(self):
        self.repo.persist(self.agg)
        self.assertEqual(self.events.count(),0)

    def test_uow_contains_events(self):
        self.repo.persist(self.agg)
        self.assertTrue(len(self.repo.uow), 1)

    def test_transaction_invokes_begin(self):
        with self.repo.transaction(self.events):
            pass
        self.assertTrue(self.repo.begin_invoked)

    def test_transaction_invokes_commit(self):
        with self.repo.transaction(self.events):
            pass
        self.assertTrue(self.repo.commit_invoked)

    def test_transaction_invokes_flush(self):
        with self.repo.transaction(self.events):
            pass
        self.assertTrue(self.repo.flush_invoked)

    def test_transaction_invokes_rollback_on_exc(self):
        try:
            with self.repo.transaction(self.events):
                raise Exception
        except Exception:
            pass
        self.assertTrue(self.repo.rollback_invoked)

    def test_transaction_not_invokes_flush_on_exc(self):
        try:
            with self.repo.transaction(self.events):
                raise Exception
        except Exception:
            pass
        self.assertTrue(not self.repo.flush_invoked)
