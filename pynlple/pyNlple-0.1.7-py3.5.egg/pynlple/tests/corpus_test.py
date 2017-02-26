# -*- coding: utf-8 -*-
import unittest
from pynlple.data.corpus import StackingSource


class StackingSourceTest(unittest.TestCase):

    def setUp(self):
        self.source1 = [
            '1', '2', '3'
        ]
        self.source2 = [
            4, 5, 6
        ]

    def test_should_return_all_items_consequently(self):
        stacking_source = StackingSource([self.source1, self.source2])
        expected_items = ['1', '2', '3', 4, 5, 6]

        self.assertEqual(expected_items, [item for item in stacking_source])
