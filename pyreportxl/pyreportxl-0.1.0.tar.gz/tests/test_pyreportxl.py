#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test_pyreportxl
---------------

Tests for `pyreportxl` module.
'''


import sys
import unittest
from contextlib import contextmanager

import click
from click.testing import CliRunner

from pyreportxl import pyreportxl
from pyreportxl import cli


class TestPyreportxl(unittest.TestCase):

    def setUp(self):
        # create cli
        @click.command()
        def main():
            pass
        self.main = main
        # create cli test object
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_000_something(self):
        pass

    def test_cli(self):
        result = self.runner.invoke(self.main, [], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
#        self.assertTrue('Usage' in result.output)
        help_result = self.runner.invoke(cli.main, ['--help'], catch_exceptions=False)
        self.assertEqual(help_result.exit_code, 0)
        self.assertTrue('Show this message and exit.' in help_result.output)
