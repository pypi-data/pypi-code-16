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
        s2 = 2*os.sep
        s5 = 5*os.sep
        s15 = 15*os.sep
        s20 = 20*os.sep
        
        start = s2+'hostname'+s+'tests'+s5+'a'+s+'b'+s+'hostname'+s2+'c'+s5+'d'+s+'tests'+s+'b'+s2+'c'
        startRef = ('SHARE', 'hostname', 'tests', 'a'+s+'b'+s+'hostname'+s+'c'+s+'d'+s+'tests'+s+'b'+s+'c')
        ret = filesysobjects.FileSysObjects.splitAppPrefix(start)
        self.assertEqual(startRef, ret) 


        top = os.path.normpath('hostname/')
        topRef = ('LFSYS', '', '', 'hostname')
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)
        self.assertEqual(topRef, ret) 


        top0ref=os.path.normpath('//hostname/tests/a/b/hostname')
        topRef = ('SHARE', 'hostname', 'tests', os.path.normpath('a/b/hostname'))
        top = filesysobjects.FileSysObjects.getTopFromPathString(top, [start])
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)

        self.assertEqual(top0ref, top) 
        self.assertEqual(topRef, ret) 
        pass


#
#######################
#

if __name__ == '__main__':
    unittest.main()

