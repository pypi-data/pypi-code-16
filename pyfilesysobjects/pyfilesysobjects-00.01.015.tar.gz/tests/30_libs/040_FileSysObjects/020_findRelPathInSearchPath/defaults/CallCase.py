from __future__ import absolute_import
from __future__ import print_function

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

import filesysobjects.FileSysObjects

#
#######################
#


class CallUnits(unittest.TestCase):

    def testCase000(self):
        try:
            px = filesysobjects.FileSysObjects.findRelPathInSearchPath() #@UnusedVariable
        except Exception as e:
            if type(e) is TypeError:
                return
            raise
        pass

    def testCase001(self):
        px = filesysobjects.FileSysObjects.findRelPathInSearchPath('')
        self.assertIsNone(px) 
        pass

    def testCase002(self):
        px = filesysobjects.FileSysObjects.findRelPathInSearchPath(None)
        self.assertIsNone(px) 
        pass

#
#######################
#

if __name__ == '__main__':
    unittest.main()

