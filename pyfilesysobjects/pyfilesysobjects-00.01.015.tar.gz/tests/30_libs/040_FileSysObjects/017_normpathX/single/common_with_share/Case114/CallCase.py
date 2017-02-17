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
    
    def testCase001(self):
#        _in = '//hostname/tests//////a/b/hostname//c////////d/tests/b///c'
        _in = r'\\hostname\tests\a/b/hostname/c/d/tests/b/c'
        _norm = r'\\hostname\tests\a/b/hostname/c/d/tests/b/c'
        self.check_normpathX(_in,_norm,'keep')

    def testCase002(self):
        _in = 'hostname////////////'
        _norm = os.path.normpath(r'hostname')
        self.check_normpathX(_in,_norm)

    def testCase003(self):
        _in = '//hostname/tests/a/b/hostname'
        _norm = os.path.normpath(r'//hostname/tests/a/b/hostname')
        self.check_normpathX(_in,_norm)




#
#######################
#

if __name__ == '__main__':
    unittest.main()

