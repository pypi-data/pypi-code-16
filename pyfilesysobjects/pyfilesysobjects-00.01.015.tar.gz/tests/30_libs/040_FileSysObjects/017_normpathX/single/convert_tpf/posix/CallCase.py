from __future__ import absolute_import
from linecache import getline


__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import os,sys
version = '{0}.{1}'.format(*sys.version_info[:2])
if version in ('2.6',): # pragma: no cover
    import unittest2 as unittest
    from unittest2 import SkipTest
elif version in ('2.7',): # pragma: no cover
    import unittest
    from unittest import SkipTest
else:
    print >>sys.stderr, "ERROR:Requires Python-2.6(.6+) or 2.7"
    sys.exit(1)

import tests.CheckNormpathX

import filesysobjects.FileSysObjects

#
#######################
#

class CallUnits(tests.CheckNormpathX.CheckNormpathX):
    
    def testCase070(self):
        _in    = 'd:/'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')
        
    def testCase071(self):
        _in    = 'd:\\'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')
        
    def testCase072(self):
        _in    = 'd:\\\\'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')

    def testCase073(self):
        _in    = 'd:\\\\\\\\'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')

    def testCase074(self):
        _in    = 'd:///'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')

    def testCase075(self):
        _in    = 'd:\\\\\\'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')

    def testCase076(self):
        _in    = 'd:///'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')

    def testCase077(self):
        _in    = 'd:\\\\\\'
        _norm  = 'd:/'

        self.check_normpathX(_in,_norm,'posix')

    def testCase080(self):
        _in    = 'd:\\/'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')

    def testCase081(self):
        _in    = 'd:\\///////'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')

    def testCase082(self):
        _in    = 'd:\\\\\\///////'
        _norm  = 'd:/'
        self.check_normpathX(_in,_norm,'posix')

    def testCase090(self):
        _in    = 'd:\\\\/\\\\/'
        _norm  = 'd:/'
#        self.check_normpathX(_in,_norm,'posix')
        self.skipTest("Intermixed single backslash/escape not (yet???) provided due to exceptions.")
        pass

    def testCase091(self):
        _in    = 'd:\\\\/\\\\///\\\\/'
        _norm  = 'd:/'
#        self.check_normpathX(_in,_norm,'posix')
        self.skipTest("Intermixed single backslash/escape not (yet???) provided due to exceptions.")
        pass


    def testCase092(self):
        _in    = 'd:\\\\/\\\\///\\\\/\\\\/\\\\////////'
        _norm  = 'd:/'
#        self.check_normpathX(_in,_norm,'posix')
        self.skipTest("Intermixed single backslash/escape not (yet???) provided due to exceptions.")
        pass

    def testCase100(self):
        _in    = 'd:\\/\\/'
        _norm  = 'd:/'
        self.skipTest("Intermixed single backslash/escape not (yet???) provided due to exceptions.")
        pass

#
#######################
#

if __name__ == '__main__':
    unittest.main()

