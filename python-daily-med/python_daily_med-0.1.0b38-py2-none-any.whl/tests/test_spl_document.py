# -*- coding: utf-8 -*-
# Copyright 2017-TODAY LasLabs Inc.
# License MIT (https://opensource.org/licenses/MIT).

import os
import unittest

from ..models.spl import SPLDocument


class TestBaseModel(unittest.TestCase):

    def setUp(self):
        xml_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'spl_doc_1.xml',
        )
        with open(xml_path, 'r') as fh:
            self.model = SPLDocument(fh.read())

    def test_init(self):
        """ It should parse XML for use as internal dict. """
        self.assertTrue(self.model['author'])
        self.assertTrue(self.model['component'])
        self.assertTrue(self.model['versionNumber'])
