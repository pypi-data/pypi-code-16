import unittest

from gophish import Gophish
from test.client import MockClient

class TestTemplates(unittest.TestCase):

    def setUp(self):
        self.client = Gophish('TEST', client=MockClient)
    
    def test_get_templates(self):
        templates = self.client.templates.get()
        self.assertEqual(len(templates), 1)

if __name__ == '__main__':
    unittest.main()
