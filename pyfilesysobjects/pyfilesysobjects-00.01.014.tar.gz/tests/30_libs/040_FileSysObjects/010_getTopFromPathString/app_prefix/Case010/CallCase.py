from __future__ import absolute_import
from linecache import getline


__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,sys

import filesysobjects.FileSysObjects
import pysourceinfo.PySourceInfo

#
#######################
#


class CallUnits(unittest.TestCase):
    """Network resources IEEE.1003.1/CIFS/SMB/UNC - respect hostname
    """

    def testCase000(self):
        """Respect 'hostname', which is actual hostname, and a node name.
        """
        s = os.sep
        s2 = 2*s
        s5 = 2*s
        s8 = 8*s
        start = s2+'hostname'+s+'tests'+s8+'a'+s+'b'+s+'hostname'+s2+'c'+s5+'d'+s+'tests'+s+'b'+s2+'c'
        top = 'hostname'+s
        top = filesysobjects.FileSysObjects.getTopFromPathString(top, [start]) #@UnusedVariable
        start = os.path.normpath(top)
        top0ref=os.path.normpath(r'//hostname/tests/a/b/hostname')

        self.assertEqual(top0ref, top) 
        pass

    def testCase001(self):
        """Respect 'hostname', which is actual hostname, and a node name.
        """
        s = os.sep
        s2 = 2*s
        s5 = 2*s
        s8 = 8*s
        start = s2+'hostname'+s+'tests'+s8+'a'+s+'b'+s+'hostname'+s2+'c'+s5+'d'+s+'tests'+s+'b'+s2+'c'
        top = 'hostname'
        top = filesysobjects.FileSysObjects.getTopFromPathString(top, [start]) #@UnusedVariable
        start = os.path.normpath(top)
        top0ref=os.path.normpath(r'//hostname/tests/a/b/hostname')

        self.assertEqual(top0ref, top) 
        pass

#
#######################
#

if __name__ == '__main__':
    unittest.main()

