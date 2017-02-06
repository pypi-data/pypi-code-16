from __future__ import absolute_import
from linecache import getline

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os
import tests.CheckEscUnesc

import filesysobjects.FileSysObjects
#
#######################
#


class CallUnits(tests.CheckEscUnesc.CheckEscUnesc):

    def testCase000(self):
        _in        = '//hostname\a\\b/c'
        _esc     = r'//hostname\\a\\b/c'
        _unesc = r'//hostname\a\b/c'
        self.check_esc_unesc(_in,_esc,_unesc,'k')
        
    def testCase010(self):
        _in        = '\\hostname/a\b/c'
        _esc     = r'\\hostname/a\\b/c'
        _unesc = r'\hostname/a\b/c'
        self.check_esc_unesc(_in,_esc,_unesc,'k')
        
    def testCase020(self):
        _in        = '\\\\hostname\a/////b\c'
        _esc     = r'\\\\hostname\\a/b\\c'
        _unesc = r'\\hostname\a/b\c'
        self.check_esc_unesc(_in,_esc,_unesc,'k')

    def testCase100(self):
        _in        = '//hostname\a\\b/c'
        _esc     = r'//hostname\\a\\b/c'
        _unesc = r'//hostname\a\b/c'
        self.check_esc_unesc(_in,_esc,_unesc,'k')

        np = filesysobjects.FileSysObjects.normpathX(_unesc)
        npx = _unesc.replace('/', os.sep)
        npx = npx.replace('\\', os.sep)
        assert np == npx
        
    def testCase110(self):
        _in        = '\\hostname/a\b/c'
        _esc     = r'\\hostname/a\\b/c'
        _unesc = r'\hostname/a\b/c'
        self.check_esc_unesc(_in,_esc,_unesc,'k')

        np = filesysobjects.FileSysObjects.normpathX(_unesc)
        npx = _unesc.replace('/', os.sep)
        npx = npx.replace('\\', os.sep)
        assert np == npx
        
    def testCase120(self):
        _in        = '\\\\hostname\a/////b\c'
        _esc     = r'\\\\hostname\\a/b\\c'
        _unesc = r'\\hostname\a/b\c'
        self.check_esc_unesc(_in,_esc,_unesc,'k')

        np = filesysobjects.FileSysObjects.normpathX(_unesc)
        npx = _unesc.replace('/', os.sep)
        npx = npx.replace('\\', os.sep)
        assert np == npx

    def testCase210(self):
        _in        = 'file://\\\\hostname\a/////b\c'
        _esc     = r'file://\\\\hostname\\a/b\\c'    #FIXME: verify this interpretation
        _unesc = r'file://\\hostname\a/b\c'     #FIXME: verify this interpretation
        self.check_esc_unesc(_in,_esc,_unesc,'k')

#
#######################
#

if __name__ == '__main__':
    unittest.main()
