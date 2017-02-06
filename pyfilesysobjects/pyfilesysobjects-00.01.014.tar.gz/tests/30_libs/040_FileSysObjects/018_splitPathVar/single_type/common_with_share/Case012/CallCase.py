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
        kargs['ias'] = False
        kargs['rtype'] = True
        kargs['rpath'] = True
        kargs['appsplit'] = True

        apstr = 'file://///hostname///////////share/a///b//c////////////////////////'
        retRef = [('file://///','hostname', 'share', 'a///b//c////////////////////////')] 
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**kargs)
        self.assertEqual(retRef, ret) 
        pass

    def testCase010(self):
        kargs = {}
        kargs['raw'] = False
        kargs['ias'] = True
        kargs['rtype'] = False
        kargs['appsplit'] = True

        apstr = 'file://///hostname///////////share/a///b//c////////////////////////'
        retRef = [('IAS','', '', filesysobjects.FileSysObjects.normpathX('/hostname/share/a/b/c'))]
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**kargs)
        self.assertEqual(retRef, ret)

    def testCase011(self):
        kargs = {}
        kargs['raw'] = False
        kargs['ias'] = True
        kargs['rtype'] = False
        kargs['appsplit'] = True

        apstr = 'file:///hostname///////////share/a///b//c////////////////////////'
        retRef = [('IAS','', '', filesysobjects.FileSysObjects.normpathX('/hostname/share/a/b/c'))]
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**kargs)
        self.assertEqual(retRef, ret)

    def testCase012(self):
        kargs = {}
        kargs['raw'] = False
        kargs['ias'] = True
        kargs['rtype'] = False
        kargs['appsplit'] = True

        apstr = 'ias:///hostname///////////share/a///b//c////////////////////////'
        retRef = [('IAS','', '', filesysobjects.FileSysObjects.normpathX('/hostname/share/a/b/c'))]
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**kargs)
        self.assertEqual(retRef, ret)

    def testCase020(self):
        kargs = {}
        kargs['raw'] = False
        kargs['ias'] = False
        kargs['rtype'] = True
        kargs['appsplit'] = True

        apstr = 'file://///hostname///////////share/a///b//c////////////////////////'
        retRef = [('file://///','hostname', 'share', os.path.normpath('a/b/c'))]
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**kargs)
        self.assertEqual(retRef, ret) 

    def testCase100(self):
        kargs = {}
        kargs['raw'] = False
        kargs['ias'] = True
        kargs['rtype'] = True
        kargs['appsplit'] = True

        apstr = 'file://///hostname///////////share/a///b//c////////////////////////'
        retRef = [('file://///','', '', os.path.normpath('/hostname/share/a/b/c'))]
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**kargs)
        self.assertEqual(retRef, ret) 

    def testCase110(self):
        kargs = {}
        kargs['ias'] = False
        kargs['rtype'] = True
        kargs['rpath'] = True
        kargs['appsplit'] = True

        s5 = 5*os.sep
        s15 = 15*os.sep
        s20 = 20*os.sep
        apstr = 'file://///hostname'+s15+'share'+os.sep+'a'+os.sep+'b'+os.sep+'c'+s15
        retRef = [('file://///','hostname', 'share', 'a'+os.sep+'b'+os.sep+'c'+s15)] 
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**kargs)
        
        self.assertEqual(retRef, ret) 

    def testCase120(self):
        kargs = {}
        kargs['raw'] = True
        kargs['ias'] = False
        kargs['appsplit'] = True

        kargs['rtype'] = True # superposed by 'raw'

        s5 = 5*os.sep
        s15 = 15*os.sep
        s20 = 20*os.sep
        apstr = 'file://///hostname'+s15+'share'+os.sep+'a'+os.sep+'b'+os.sep+'c'+s15
        retRef = [('RAW', '', '', 'file://///hostname'+s15+'share'+os.sep+'a'+os.sep+'b'+os.sep+'c'+s15)]
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**kargs)
        self.assertEqual(retRef, ret) 
        pass

#
#######################
#

if __name__ == '__main__':
    unittest.main()

