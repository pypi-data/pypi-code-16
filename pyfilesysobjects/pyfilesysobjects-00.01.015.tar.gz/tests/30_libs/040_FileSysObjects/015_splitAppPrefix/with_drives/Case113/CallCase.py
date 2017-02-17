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
        
        start = os.path.normpath('//hostname/tests//////a/b/hostname//c////////d/tests/b///c')
        startRef = ('SHARE', 'hostname', 'tests', os.path.normpath('a/b/hostname/c/d/tests/b/c'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(start)
        self.assertEqual(startRef, ret) 


        top = os.path.normpath('/hostname')
        topRef = ('LFSYS', '', '', os.path.normpath('/hostname'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)
        self.assertEqual(topRef, ret) 


        top0ref=os.path.normpath('//hostname/tests/a/b/hostname')
        topRef = ('SHARE', 'hostname', 'tests', os.path.normpath('a/b/hostname'))
        top = filesysobjects.FileSysObjects.getTopFromPathString(top, [start], **{'ias':True})
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)

        self.assertEqual(top0ref, top) 
        self.assertEqual(topRef, ret) 
        pass

    def testCase020(self):
        
        start = os.path.normpath('//hostname/tests//////a/b/hostname//c////////d/tests/b///c')
        startRef = ('SHARE', 'hostname', 'tests', os.path.normpath('a/b/hostname/c/d/tests/b/c'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(start)
        self.assertEqual(startRef, ret) 


        top = os.path.normpath('/hostname')
        topRef = ('LFSYS', '', '', os.path.normpath('/hostname'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)
        self.assertEqual(topRef, ret) 


        top0ref=os.path.normpath('//hostname/tests/a/b/hostname')
        topRef = ('SHARE', 'hostname', 'tests', os.path.normpath('a/b/hostname'))
        top = filesysobjects.FileSysObjects.getTopFromPathString(top, [start])
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)

        self.assertEqual(top0ref, top) 
        self.assertEqual(topRef, ret) 
        pass

    def testCase030(self):
        
        start = os.path.normpath('//hostname/hostname/tests//////a/b/hostname//c////////d/tests/b///c')
        startRef = ('SHARE', 'hostname', 'hostname', os.path.normpath('tests/a/b/hostname/c/d/tests/b/c'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(start)
        self.assertEqual(startRef, ret) 

        top = os.path.normpath('/hostname')
        topRef = ('LFSYS', '', '', os.path.normpath('/hostname'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)
        self.assertEqual(topRef, ret) 


    def testCase040(self):
        
        start = 'smb://'+os.path.normpath('hostname/hostname/tests//////a/b/hostname//c////////d/tests/b///c')
        startRef = ('SMB', 'hostname', 'hostname', os.path.normpath('tests/a/b/hostname/c/d/tests/b/c'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(start)
        self.assertEqual(startRef, ret) 

        top = os.path.normpath('/hostname')
        topRef = ('LFSYS', '', '', os.path.normpath('/hostname'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(top)
        self.assertEqual(topRef, ret) 

        top0ref='smb://'+os.path.normpath('hostname/hostname/tests/a/b/hostname')
        topRef = ('SMB', 'hostname', 'hostname', os.path.normpath('tests/a/b/hostname'))
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

