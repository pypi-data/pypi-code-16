from unittest import TestCase
from concurapi.client import ConcurAPI


class TestConcurAPI(TestCase):
    def test_initialization(self):
        with self.assertRaises(KeyError):
            ConcurAPI()

    def test_should_initialize_correctly(self):
        client = ConcurAPI(client_key="Test",
                           client_secret="Secret",
                           username="Test",
                           password="Hello")
        self.assertIsNotNone(client)