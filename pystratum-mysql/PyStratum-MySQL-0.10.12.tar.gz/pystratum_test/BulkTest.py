"""
PyStratum
"""
import sys

from pystratum_test.TestBulkHandler import TestBulkHandler
from pystratum_test.TestDataLayer import TestDataLayer
from pystratum_test.StratumTestCase import StratumTestCase


class BulkTest(StratumTestCase):
    # ------------------------------------------------------------------------------------------------------------------
    def test1(self):
        """
        Stored routine with designation type none must return the number of rows affected.
        """
        bulk_handler = TestBulkHandler()
        n = TestDataLayer.tst_test_bulk(bulk_handler)

        self.assertEqual(3, n)

        output = sys.stdout.getvalue().strip()
        print(output)
        self.assertEqual(output,'start\n1\n2\n3\nstop')

# ----------------------------------------------------------------------------------------------------------------------
