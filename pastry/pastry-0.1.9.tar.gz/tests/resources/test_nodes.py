import mock
import unittest

from pastry.resources.nodes import Nodes


class NodesTestCase(unittest.TestCase):

    @mock.patch('pastry.resources.nodes.Base.exists', return_value=True)
    def test_exists(self, base):
        self.assertEqual(Nodes.exists('node'), True)
