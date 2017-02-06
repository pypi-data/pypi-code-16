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
    
    def testCase000(self):
        _in    = '\a'
        _norm  = r'\a' 
        self.check_normpathX(_in,_norm,'win')

    def testCase001(self):
        _in    = 'd:/a/b/c'
        _norm  = os.path.normpath('d:\\'+'a\\'+'b\c')  # used as an unaltered reference, thus prep it
        self.check_normpathX(_in,_norm,'win')

    def testCase080(self):
        _in        = 'd:/'
        _norm  = 'd:\\'
        self.check_normpathX(_in,_norm,'win')
        
    def testCase081(self):
        _in        = 'd:\\'
        _norm  = os.path.normpath('d:\\' )
        self.check_normpathX(_in,_norm,'win')
        
    def testCase082(self):
        _in        = 'd:///'
        _norm  = os.path.normpath('d:\\')
        self.check_normpathX(_in,_norm,'win')

    def testCase083(self):
        _in        = 'd:\\\\\\'
        _norm  = os.path.normpath('d:\\')
        self.check_normpathX(_in,_norm,'win')

    def testCase084(self):
        _in        = 'd:///'
        _norm  = os.path.normpath('d:\\')
        self.check_normpathX(_in,_norm,'win')

    def testCase085(self):
        _in        = 'd:\\\\\\'
        _norm  = os.path.normpath('d:\\')
        self.check_normpathX(_in,_norm,'win')

    def testCase088(self):
        _in        = 'd:\\/'
        _norm  = os.path.normpath('d:\\')
        self.check_normpathX(_in,_norm,'win')

    def testCase089(self):
        _in        = 'd:\\\\/\\\\///\\\\//////////'
        _norm  = os.path.normpath('d:\\')
#        self.check_normpathX(_in,_norm,'win')
        self.skipTest("Intermixed single backslash/escape not (yet???) provided due to exceptions.")

    def testCase090(self):
        _in        = 'd:/a\b/c'
        _norm  = os.path.normpath('d:/a/b/c')
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

