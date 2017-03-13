# -*- coding: utf-8 -*-

from .context import reverpf

import unittest
import sys

class TestCLI(unittest.TestCase):
    """ Test CLI """
    @classmethod
    def setUpClass(cls):
        parser = reverpf.build_parser()
        cls.parser = parser

class TestCLITest(TestCLI):

    def test_simple_case(self):
        fmt = '%02d%03d'
        finput = './tests/file.txt'
        options = self.parser.parse_args(['-f', fmt, '-i', finput])
        reverpf.rever(options.file, options.fmt, options.sep)
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        output = sys.stdout.getvalue().strip() # because stdout is an StringIO instance
        self.assertEquals(output,';01;002;')
