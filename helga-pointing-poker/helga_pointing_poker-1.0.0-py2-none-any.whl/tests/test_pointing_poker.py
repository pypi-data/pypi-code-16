import sys
import unittest
try:
    from unittest import mock
except ImportError:
    from mock import mock
from mongomock import MongoClient
sys.modules['helga.plugins'] = mock.Mock() # hack to avoid py3 errors in test
from helga.db import db
from helga_pointing_poker.helga_pointing_poker import logic


class Testpointing_poker(unittest.TestCase):
    def setUp(self):
        self.db_patch = mock.patch(
            'pymongo.MongoClient',
            new_callable=lambda: MongoClient
        )
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)

    def tearDown(self):
        db.helga_poker.drop()

    def test_pointing_poker(self):
        logic(['point', '1', '3'], 'narfman0')
        logic(['point', '1', '3'], 'scubasteve')
        logic(['point', '1', '2'], 'taimaishu')
        result = logic(['status', '1'], None)
        self.assertIn('3 votes', result)
        result = logic(['show', '1'], None)
        self.assertIn('Median:3', result)
        self.assertIn('avg:2.66', result)
        result = logic(['yo'], None)
        self.assertIn('Unrecognized', result)


if __name__ == '__main__':
    unittest.main()
