from __future__ import absolute_import

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import tests.CheckEscUnesc

import filesysobjects.FileSysObjects

#
#######################
#


class CallUnits(tests.CheckEscUnesc.CheckEscUnesc):

    def testCase110(self):
        _in        = '//a/a/b/c'
        _esc     = r'\\\\a\\a\\b\\c'
        _unesc = r'\\a\a\b\c'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase112(self):
        _in        = r'//a/a/b/c'
        _esc     = r'\\\\a\\a\\b\\c'
        _unesc = r'\\a\a\b\c'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase113(self):
        _in        = r'/a/a//b/c'
        _esc     = r'\\a\\a\\b\\c'
        _unesc = r'\a\a\b\c'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase114(self):
        _in        = '//a/////a//////b/c'
        _esc     = r'\\\\a\\a\\b\\c'
        _unesc = r'\\a\a\b\c'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase115(self):
        _in        = '//a/a///b/c'
        _esc     = r'\\\\a\\a\\b\\c'
        _unesc = r'\\a\a\b\c'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase116(self):
        _in        = '/a/a////b/c'
        _esc     = r'\\a\\a\\b\\c'
        _unesc = r'\a\a\b\c'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase120(self):
        _in        = '//t/v//n'
        _esc     = r'\\\\t\\v\\n'
        _unesc = r'\\t\v\n'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase130(self):
        _in        = '\//' 'x/' 'x' '/x'
        _esc     = r'\\\\x\\x\\x'
        _unesc = r'\\x\x\x'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase131(self):
        _in        = '//a/a//a'
        _esc     = r'\\\\a\\a\\a'
        _unesc = r'\\a\a\a'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase132(self):
        _in        = '//b/b///b'
        _esc     = r'\\\\b\\b\\b'
        _unesc = r'\\b\b\b'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase133(self):
        _in        = '//f/f//f'
        _esc     = r'\\\\f\\f\\f'
        _unesc = r'\\f\f\f'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')
    
    def testCase134(self):
        _in        = '//n/n//n'
        _esc     = r'\\\\n\\n\\n'
        _unesc = r'\\n\n\n'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')
        
    def testCase135(self):
        _in        = '//r/r/r'
        _esc     = r'\\\\r\\r\\r'
        _unesc = r'\\r\r\r'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')
        
    def testCase136(self):
        _in        = '//t/t///t'
        _esc     = r'\\\\t\\t\\t'
        _unesc = r'\\t\t\t'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

#
#######################
#

if __name__ == '__main__':
    unittest.main()
