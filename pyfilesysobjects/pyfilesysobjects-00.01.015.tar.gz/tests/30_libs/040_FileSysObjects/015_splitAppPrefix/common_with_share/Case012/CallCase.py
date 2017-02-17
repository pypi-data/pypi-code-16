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

#
#######################
#


class CallUnits(unittest.TestCase):
    """Split network resources IEEE.1003.1/CIFS/SMB/UNC/URI
    """


    def testCase000(self):
        kargs = {}
        kargs['raw'] = True
        kargs['ias'] = False
        kargs['rtype'] = False

        apstr = 'file://///hostname///////////share/a///b//c////////////////////////'
        retRef = ('file://///','hostname', 'share', 'a///b//c////////////////////////') 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**kargs)
        self.assertEqual(retRef, ret) 

    def testCase010(self):
        kargs = {}
        kargs['raw'] = False
        kargs['ias'] = True
        kargs['rtype'] = False

        apstr = 'file://///hostname///////////share/a///b//c////////////////////////'
        retRef = ('IAS','', '', os.path.normpath('hostname/share/a/b/c')) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**kargs)
        self.assertEqual(retRef, ret) 

    def testCase020(self):
        kargs = {}
        kargs['raw'] = False
        kargs['ias'] = False
        kargs['rtype'] = True

        apstr = 'file://///hostname///////////share/a///b//c////////////////////////'
        retRef = ('file://///','hostname', 'share', os.path.normpath('a/b/c'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**kargs)
        self.assertEqual(retRef, ret) 

    def testCase100(self):
        kargs = {}
        kargs['raw'] = False
        kargs['ias'] = True
        kargs['rtype'] = True

        apstr = 'file://///hostname///////////share/a///b//c////////////////////////'
        retRef = ('IAS','', '', os.path.normpath('hostname/share/a/b/c'))
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**kargs)
        self.assertEqual(retRef, ret) 

    def testCase110(self):
        kargs = {}
        kargs['raw'] = True
        kargs['ias'] = False
        kargs['rtype'] = True

        s5 = 5*os.sep
        s15 = 15*os.sep
        s20 = 20*os.sep
        apstr = 'file://///hostname'+s15+'share'+os.sep+'a'+os.sep+'b'+os.sep+'c'+s15
        retRef = ('file://///','hostname', 'share', 'a'+os.sep+'b'+os.sep+'c'+s15) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**kargs)
        
        self.assertEqual(retRef, ret) 

    def testCase120(self):
        kargs = {}
        kargs['raw'] = True
        kargs['ias'] = True
        kargs['rtype'] = True

        s5 = 5*os.sep
        s15 = 15*os.sep
        s20 = 20*os.sep
        apstr = 'file://///hostname'+s15+'share'+os.sep+'a'+os.sep+'b'+os.sep+'c'+s15
        retRef = ('IAS', '', '', 'hostname'+s15+'share'+os.sep+'a'+os.sep+'b'+os.sep+'c'+s15)
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr,**kargs)
        self.assertEqual(retRef, ret) 

#
#######################
#

if __name__ == '__main__':
    unittest.main()

