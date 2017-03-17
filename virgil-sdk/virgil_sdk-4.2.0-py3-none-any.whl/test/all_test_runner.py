import unittest
from unittest import TextTestRunner

from test.cryptography import crypto_test
from test.cryptography import compatibility_test
from test.client import virgil_client_test
from test.client import request_signer_test
from test.storage import default_storage_test
from test.api import test_virgil_buffer
from test.api import test_virgil_key
from test.api import test_virgil_card
from test.api import test_key_manager
from test.api import test_card_manager


def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(crypto_test))
    suite.addTests(loader.loadTestsFromModule(compatibility_test))
    suite.addTests(loader.loadTestsFromModule(virgil_client_test))
    suite.addTests(loader.loadTestsFromModule(request_signer_test))
    suite.addTests(loader.loadTestsFromModule(default_storage_test))
    suite.addTests(loader.loadTestsFromModule(test_virgil_buffer))
    suite.addTests(loader.loadTestsFromModule(test_virgil_key))
    suite.addTests(loader.loadTestsFromModule(test_virgil_card))
    suite.addTests(loader.loadTestsFromModule(test_key_manager))
    suite.addTests(loader.loadTestsFromModule(test_card_manager))
    return suite

if __name__ == '__main__':
    unittest.main()
