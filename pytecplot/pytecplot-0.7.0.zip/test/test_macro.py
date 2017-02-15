from __future__ import unicode_literals, with_statement

import ctypes
import numpy as np
import os
import platform
import re
import sys

from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from textwrap import dedent

import unittest
from unittest.mock import patch, Mock, PropertyMock

from test import patch_tecutil

import tecplot as tp
from tecplot.exception import TecplotMacroError


class TestMacros(unittest.TestCase):
    def test_execute_file(self):
        tp.new_layout()
        with NamedTemporaryFile(mode='wt', suffix='.mcr', delete=False) as ftmp:
            ftmp.write(dedent('''\
                #!MC 1410
                $!CREATERECTANGULARZONE
                  IMAX = 10
                  JMAX = 10
                  KMAX = 10
                  X1 = 0
                  Y1 = 0
                  Z1 = 0
                  X2 = 1
                  Y2 = 1
                  Z2 = 1
                  XVAR = 1
                  YVAR = 2
                  ZVAR = 3
            '''))
            ftmp.close()
            tp.macro.execute_file(ftmp.name)
            os.remove(ftmp.name)
        ds = tp.active_frame().dataset
        self.assertEqual(ds.num_zones, 1)
        self.assertEqual(ds.num_variables, 3)

        with NamedTemporaryFile(mode='wt', suffix='.mcr', delete=False) as ftmp:
            ftmp.write(dedent('''\
                $!bad macro command
            '''))
            ftmp.close()
            with self.assertRaises(TecplotMacroError):
                tp.macro.execute_file(ftmp.name)
            os.remove(ftmp.name)

    def test_execute_command(self):
        tp.new_layout()
        tp.macro.execute_command('''
            $!CREATERECTANGULARZONE
              IMAX = 10
              JMAX = 10
              KMAX = 10
              X1 = 0
              Y1 = 0
              Z1 = 0
              X2 = 1
              Y2 = 1
              Z2 = 1
              XVAR = 1
              YVAR = 2
              ZVAR = 3
        ''')
        ds = tp.active_frame().dataset
        self.assertEqual(ds.num_zones, 1)
        self.assertEqual(ds.num_variables, 3)

        with self.assertRaises(TecplotMacroError):
            tp.macro.execute_command('$!bad macro command')

    def test_execute_extended_command(self):
        tp.new_layout()
        tp.active_page().add_frame()
        tp.active_page().add_frame()
        tp.active_page().add_frame()
        tp.macro.execute_extended_command('Multi Frame Manager',
                                          'TILEFRAMESSQUARE')
        with self.assertRaises(TecplotMacroError):
            tp.macro.execute_extended_command('bad procid', 'bad command')

    def test_comments(self):
        cmts = re.compile(r'(?<!\\)(\".*?\"|\'.*?\')|(#[^\r\n]*$)', re.M)
        data = r'''testing # comment
# whole line comment
x = 'testing' # 'comment'
"'one', 'two' # not a comment " # comment
" \' # not a comment " # comment
\' that's not a string. # comment inside a string ' # that's a comment
$! blah blah
    'blah ' blah, 'blah' # comment
   'testing # comment'''
        data_no_comments = cmts.sub(lambda m: m.group(1) or '', data)
        self.assertEqual(data_no_comments, 'testing \n\nx = \'testing\' \n"\'one\', \'two\' # not a comment " \n" \\\' # not a comment " \n\\\' that\'s not a string. # comment inside a string \' \n$! blah blah\n    \'blah \' blah, \'blah\' \n   \'testing ')
        tp.macro.execute_command('# just a comment')


if __name__ == '__main__':
    from . import main
    main()
