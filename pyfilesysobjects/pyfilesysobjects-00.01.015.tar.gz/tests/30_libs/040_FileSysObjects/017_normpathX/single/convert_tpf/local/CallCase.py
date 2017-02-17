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
import tests.CheckNormpathX

import filesysobjects.FileSysObjects

#
#######################
#

class CallUnits(tests.CheckNormpathX.CheckNormpathX):
    
    def testCase000(self):
        _in    = '\\a'
        _norm  = os.path.normpath('\\a')
        self.check_normpathX(_in,_norm,'local')

    def testCase001(self):
        _in    = '\a'
        _norm  = os.path.normpath('\a')
        self.check_normpathX(_in,_norm,'local')

    def testCase002(self):
        _in    = r'\a'
        _norm  = os.path.normpath(r'\a')
        self.check_normpathX(_in,_norm,'local')

    def testCase010(self):
        _in    = 'd:\\a'
        _norm  = os.path.normpath('d:\\a')
        self.check_normpathX(_in,_norm,'local')

    def testCase011(self):
        _in    = 'd:\a'
        _norm  = os.path.normpath('d:\a')
        self.check_normpathX(_in,_norm,'local')

    def testCase012(self):
        _in    = 'd:/a'
        _norm  = os.path.normpath('d:/a')
        self.check_normpathX(_in,_norm,'local')

    def testCase020(self):
        _in    = 'd:\\'
        _norm  = os.path.normpath('d:\\')
        self.check_normpathX(_in,_norm,'local')

    def testCase021(self):
        _in    = 'd:/'
        _norm  = os.path.normpath('d:/')
        self.check_normpathX(_in,_norm,'local')

    def testCase030(self):
        _in    = '/a/b/c'
        _norm  = os.path.normpath('/a/b/c')
        self.check_normpathX(_in,_norm,'local')


#
#######################
#

if __name__ == '__main__':
    unittest.main()

