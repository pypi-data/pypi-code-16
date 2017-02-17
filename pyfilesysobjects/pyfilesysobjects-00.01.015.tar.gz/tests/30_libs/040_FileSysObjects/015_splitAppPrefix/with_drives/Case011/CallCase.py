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
        apstr = 'd:/a/b/c'
        retRef = ('LDSYS','', 'd:', os.path.normpath('/a/b/c')) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)
        self.assertEqual(retRef, ret) 
        
    def testCase010(self):
        apstr = os.path.normpath('d:a/b/c')
        retRef = ('LDSYS','', 'd:', filesysobjects.FileSysObjects.escapeFilePath(os.path.normpath('a/b/c'))) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)

        ret = (ret[0], ret[1], ret[2], filesysobjects.FileSysObjects.escapeFilePath(ret[3]) ) 

        self.assertEqual(retRef, ret) 
        

    def testCase020(self):
        apstr = 'd:'
        retRef = ('LDSYS','', 'd:', '') 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)
        self.assertEqual(retRef, ret) 

    def testCase030(self):
        apstr = 'd:'+os.path.normpath('/')
        retRef = ('LDSYS','', 'd:', os.path.normpath('/')) 
        ret = filesysobjects.FileSysObjects.splitAppPrefix(apstr)
        self.assertEqual(retRef, ret) 

#
#######################
#

if __name__ == '__main__':
    unittest.main()

