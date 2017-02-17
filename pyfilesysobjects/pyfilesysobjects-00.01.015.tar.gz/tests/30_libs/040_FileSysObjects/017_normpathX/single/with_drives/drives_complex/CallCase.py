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
        s = os.sep
        s10 = 10*os.sep
        _in = 'd:'+s+'a'+s10+'b'+s+'c'
        _norm  = os.path.normpath('d:/a/b/c')
        self.check_normpathX(_in,_norm)
        
    def testCase010(self):
        s = os.sep
        s10 = 10*os.sep
        _in = 'd:'+s+'a'+s10+'b'+s+'c'
        _norm  = os.path.normpath('d:/a/b/c')
        self.check_normpathX(_in,_norm)

    def testCase020(self):
        s = os.sep
        s7 = 7*os.sep
        _in = 'd:'+s+'a'+s7+'b'+s+'c'
        _norm  = os.path.normpath('d:/a/b/c')
        self.check_normpathX(_in,_norm)

    def testCase030(self):
        s = os.sep
        s7 = 7*os.sep
        _in = 'd:'+s+'a'+s+'b'+s7+'c'
        _norm  = os.path.normpath('d:/a/b/c')
        self.check_normpathX(_in,_norm)

    def testCase050(self):
        s = os.sep
        _in = 'd:'+s
        _norm  = os.path.normpath('d:\\')
        self.check_normpathX(_in,_norm,'win')

    def testCase060(self):
        s = os.sep
        s7 = 7*os.sep #@UnusedVariable
        s10 = 10*os.sep #@UnusedVariable
        _in = 'd:'+s
        _norm  = _in
        self.check_normpathX(_in,_norm)

    def testCase061(self):
        _in = 'd://hostname/tests//////a/b/hostname//c////////d/tests/b///c'
        _norm = 'd:/hostname/tests/a/b/hostname/c/d/tests/b/c'
        self.check_normpathX(_in,_norm,'cnp')

    def testCase062(self):
        _in = 'd://hostname/tests//////a/b/hostname//c////////d/tests/b///c'
        _norm = 'd:/hostname/tests/a/b/hostname/c/d/tests/b/c'
        self.check_normpathX(_in,_norm,'posix')

    def testCase063(self):
        _in = 'hostname/'
        _norm = os.path.normpath('hostname')
        self.check_normpathX(_in,_norm)

    def testCase064(self):
        _in = 'd:/hostname/'
        _norm = 'd:/hostname'
        self.check_normpathX(_in,_norm,'posix')



#
#######################
#

if __name__ == '__main__':
    unittest.main()

