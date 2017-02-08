import mock
import unittest

from pastry.resources.base import Base


class BaseTestCase(unittest.TestCase):

    def test_base_url(self):
        Base._base_url = 'url'
        self.assertEqual(Base.base_url(), 'url')
        Base._base_url = None
        self.assertRaises(ValueError, Base.base_url)

    @mock.patch('pastry.resources.base.Base.base_url')
    @mock.patch('pastry.resources.base.PastryClient')
    def test_all(self, pastry_client, base_url):
        pastry_client.call.return_value = 'result'
        self.assertEqual(Base.index(), 'result')
