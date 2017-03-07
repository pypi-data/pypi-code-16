"""
PyStratum
"""
import sys
import unittest
from io import StringIO

from pystratum_test.TestDataLayer import TestDataLayer


class StratumTestCase(unittest.TestCase):
    # ------------------------------------------------------------------------------------------------------------------
    def setUp(self):
        TestDataLayer.config['host'] = 'localhost'
        TestDataLayer.config['user'] = 'test'
        TestDataLayer.config['password'] = 'test'
        TestDataLayer.config['database'] = 'test'

        TestDataLayer.connect()

        self.held, sys.stdout = sys.stdout, StringIO()

    # ------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        sys.stdout = self.held
        TestDataLayer.disconnect()

# ----------------------------------------------------------------------------------------------------------------------
