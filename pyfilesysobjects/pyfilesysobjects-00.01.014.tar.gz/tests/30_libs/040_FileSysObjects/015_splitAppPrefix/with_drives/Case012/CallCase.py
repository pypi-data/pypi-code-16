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

    def testCase000(self):
        s = os.sep
        s10 = 10*os.sep
        apstr = 'd:'+s+'a'+s10+'b'+s+'c'
        retRef = ('LDSYS','', 'd:', os.path.normpath('/a/b/c')) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)
        self.assertEqual(retRef, ret) 
        
    def testCase010(self):
        s = os.sep
        s10 = 10*os.sep
        apstr = 'd:'+s+'a'+s10+'b'+s+'c'
        retRef = ('LDSYS','', 'd:', os.path.normpath('/a/b/c')) #FIXME: for whatever reason... 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)     
        self.assertEqual(retRef, ret) 

    def testCase020(self):
        s = os.sep
        s7 = 7*os.sep
        s10 = 10*os.sep
        apstr = 'd:'+s+'a'+s7+'b'+s+'c'
        retRef = ('LDSYS','', 'd:', os.path.normpath('/a/b/c')) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)
        self.assertEqual(retRef, ret) 

    def testCase030(self):
        s = os.sep
        s7 = 7*os.sep
        s10 = 10*os.sep
        apstr = 'd:'+s+'a'+s+'b'+s7+'c'
        retRef = ('LDSYS','', 'd:', os.path.normpath('/a/b/c')) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)
        self.assertEqual(retRef, ret) 

    def testCase050(self):
        s = os.sep
        s7 = 7*os.sep
        s10 = 10*os.sep
        apstr = 'd:'+s
        retRef = ('LDSYS','', 'd:', os.path.normpath('/')) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)
        self.assertEqual(retRef, ret) 

    def testCase060(self):
        s = os.sep
        s7 = 7*os.sep
        s10 = 10*os.sep
        apstr = 'd:'+s
        retRef = ('LDSYS','', 'd:', os.path.normpath('/')) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)
        self.assertEqual(retRef, ret) 

#
#######################
#

if __name__ == '__main__':
    unittest.main()

