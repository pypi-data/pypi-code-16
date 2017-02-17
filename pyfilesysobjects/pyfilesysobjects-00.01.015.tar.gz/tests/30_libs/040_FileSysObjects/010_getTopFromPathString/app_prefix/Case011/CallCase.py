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
        
        start = '//hostname/tests//////a/b/hostname//c////////d/tests/b///c'
        top = 'hostname/'
        top = filesysobjects.FileSysObjects.getTopFromPathString(top, [start]) #@UnusedVariable
        top0ref=os.path.normpath('//hostname/tests/a/b/hostname')
        top=os.path.normpath(top)

        self.assertEqual(top0ref, top) 
        pass


#
#######################
#

if __name__ == '__main__':
    unittest.main()

