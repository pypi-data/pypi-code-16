# -*- coding: utf-8 -*-
# Copyright 2017-TODAY LasLabs Inc.
# License MIT (https://opensource.org/licenses/MIT).

import os
import unittest

from ..models.spl_document import parse, get_all_values


class TestSPLDocument(unittest.TestCase):

    TEST_FILES = [
        'spl_doc_1.xml',
        'spl_doc_1.xml',
    ]
    TEST_DIR = os.path.abspath(os.path.dirname(__file__))

    def _parse_file(self, test_file):
        return parse(os.path.join(self.TEST_DIR, test_file))

    def test_parse(self):
        """ It should parse the sample files without errors. """
        for test_file in self.TEST_FILES:
            spl_doc = self._parse_file(test_file)
            self.assertTrue(spl_doc.id.root)
            self.assertTrue(spl_doc.title)
            self.assertTrue(spl_doc.code.code)

    def test_get_all_values(self):
        """ It should return a list of the node values. """
        spl_doc = self._parse_file(self.TEST_FILES[0])
        expect = ['RENESE', '\n\t\t', '\n\t\t', '(polythiazide)',
                  '\n\t\t', 'TABLETS', '\n\t\t', 'for Oral Administration']
        self.assertEqual(
            get_all_values(expect.title.content_), expect,
        )
