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
        
        start = filesysobjects.FileSysObjects.normpathX('hostname/tests//////a/b/hostname//c////////d/tests/b///c')
        startRef = ('LFSYS', '', '',filesysobjects.FileSysObjects.normpathX( 'hostname/tests/a/b/hostname/c/d/tests/b/c'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(start)
        self.assertEqual(startRef, ret) 


        top = filesysobjects.FileSysObjects.normpathX('hostname')
        topRef = ('LFSYS', '', '', filesysobjects.FileSysObjects.normpathX('hostname'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)
        self.assertEqual(topRef, ret) 
        pass

    def testCase020(self):
        
        start = filesysobjects.FileSysObjects.normpathX('hostname/tests//////a/b/hostname//c////////d/tests/b///c')
        startRef = ('LFSYS', '', '', filesysobjects.FileSysObjects.normpathX('hostname/tests/a/b/hostname/c/d/tests/b/c'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(start)
        self.assertEqual(startRef, ret) 


        top = filesysobjects.FileSysObjects.normpathX('hostname')
        topRef = ('LFSYS', '', '', filesysobjects.FileSysObjects.normpathX('hostname'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)
        self.assertEqual(topRef, ret) 


        top=filesysobjects.FileSysObjects.normpathX('hostname/tests/a/b/hostname')
        topRef = ('LFSYS', '', '', filesysobjects.FileSysObjects.normpathX('hostname/tests/a/b/hostname'))
        top = filesysobjects.FileSysObjects.getTopFromPathString(top, [start])
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)

        self.assertEqual(topRef, ret) 
        pass

if __name__ == '__main__':
    unittest.main()

