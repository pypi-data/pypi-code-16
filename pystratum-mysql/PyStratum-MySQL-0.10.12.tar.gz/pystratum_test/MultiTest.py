"""
PyStratum
"""
from pystratum_test.TestDataLayer import TestDataLayer
from pystratum_test.StratumTestCase import StratumTestCase


class MultiTest(StratumTestCase):
    # ------------------------------------------------------------------------------------------------------------------
    def test1(self):
        """
        Stored routine with designation type multi must return a list of list.
        """
        ret = TestDataLayer.tst_test_multi()
        self.assertIsInstance(ret, list)

        # We must have 2 result sets.
        self.assertEqual(2, len(ret))

        # First result set must have 1 row.
        self.assertIsInstance(ret[0], list)
        self.assertEqual(1, len(ret[0]))

        # Second result set must have 2 rows.
        self.assertIsInstance(ret[1], list)
        self.assertEqual(2, len(ret[1]))


# ----------------------------------------------------------------------------------------------------------------------
