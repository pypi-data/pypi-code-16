#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from showcase import utils


class TestProbablyText(unittest.TestCase):
    def path_to(self, fname):
        return os.path.join(os.path.dirname(__file__), 'data', fname)

    def check_file(self, fname, expected=True):
        self.assertEqual(
            utils.is_probably_text(self.path_to(fname)), expected,
        )

    def test_text(self):
        self.check_file('test.txt')

    def test_text_no_ext(self):
        self.check_file('test')

    def test_unicode(self):
        self.check_file('test_unicode')

    def test_md(self):
        self.check_file('test.md')

    def test_rst(self):
        self.check_file('test.rst')

    def test_json(self):
        self.check_file('test.json')

    def test_csv(self):
        self.check_file('test.csv')

    def test_tsv(self):
        self.check_file('test.tsv')

    def test_png(self):
        self.check_file('test.png', False)
