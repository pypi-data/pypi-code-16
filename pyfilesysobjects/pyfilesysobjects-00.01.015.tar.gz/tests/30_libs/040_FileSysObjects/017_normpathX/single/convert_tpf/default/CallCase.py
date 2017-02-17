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
    
    def testCase002(self):
        _in    = 'd:a\b\c'
        _norm  = os.path.normpath('d:a/b/c') 
        self.check_normpathX(_in,_norm)

    def testCase010(self):
        _in    = 'd:'
        _norm  = os.path.normpath('d:' )
        self.check_normpathX(_in,_norm)

    def testCase091(self):
        _in        = 'd:a\b\c'
        _norm  = os.path.normpath('d:a/b/c')
        self.check_normpathX(_in,_norm)


#
#######################
#

if __name__ == '__main__':
    unittest.main()

