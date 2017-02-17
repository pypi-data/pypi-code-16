import datetime

from huey.constants import EmptyData
from huey.contrib.sqlitedb import SqliteHuey
from huey.contrib.sqlitedb import SqliteStorage
from huey.tests.base import HueyTestCase


sqlite_huey = SqliteHuey('/tmp/sqlite-huey.db')


class TestSqliteStorage(HueyTestCase):
    def get_huey(self):
        return sqlite_huey

    def test_enqueue_dequeue_results(self):
        @self.huey.task()
        def test_queues_add(k, v):
            return k + v

        db = self.huey.storage
        self.assertTrue(isinstance(db, SqliteStorage))

        res = test_queues_add(3, 4)
        self.assertEqual(db.queue_size(), 1)

        task = self.huey.dequeue()
        self.huey.execute(task)
        self.assertEqual(db.result_store_size(), 1)
        self.assertEqual(res.get(), 7)
        self.assertEqual(db.queue_size(), 0)
        self.assertEqual(db.result_store_size(), 0)

    def test_schedule(self):
        pass
