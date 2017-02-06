from __future__ import absolute_import


__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,sys #@UnusedImport

from filesysobjects.FileSysObjects import  escapeFilePath,unescapeFilePath


#
#######################
#


class CallUnits(unittest.TestCase):

    def testCase000(self):
        apstr = 'a/b/c'
        apstrRef = 'a\\\\b\\\\c'
        ret = escapeFilePath(apstr,'b')
        self.assertEqual(apstrRef,ret) 
        
        apstrRaw = r'a\b\c' # avoids interpretation by re itself of '\b'
        ret0 = unescapeFilePath(ret)
        self.assertEqual(ret0,apstrRaw) 

    def testCase001(self):
        apstr = 'a/b/c'
        apstrRef = 'a\\\\b\\\\c'
        ret = escapeFilePath(apstr,'b')
        self.assertEqual(apstrRef,ret) 

        apstrRaw = r'a\b\c' # avoids interpretation by re itself of '\b'
        ret0 = unescapeFilePath(ret)
        self.assertEqual(ret0,apstrRaw) 

        
    def testCase002(self):
        apstr = 'a/b/c'
        apstrRef = r'a\b\c'
        
        ret = escapeFilePath(apstr,'b')
        ret = unescapeFilePath(ret)
        self.assertEqual(apstrRef,ret) 

    def testCase010(self):
        apstr = '/a/b/c'
        apstrRef = r'\a\b\c'
        ret = escapeFilePath(apstr,'b')
        ret = unescapeFilePath(ret)
        self.assertEqual(apstrRef, ret) 

    def testCase020(self):
        apstr = 'a'
        ret = escapeFilePath(apstr,'b')
        ret = unescapeFilePath(ret)
        self.assertEqual(apstr, ret) 

    def testCase030(self):
        apstr = '/'
        apstrRef = '\\'
        ret = escapeFilePath(apstr,'b')
        ret = unescapeFilePath(ret)
        self.assertEqual(apstrRef, ret) 

    def testCase035(self):
        apstr = '/'
        apstrRef = '\\'
        ret = escapeFilePath(apstr,'b')
        ret = unescapeFilePath(ret)
        self.assertEqual(apstrRef, ret) 

    def testCase040(self):
        apstr = ''
        ret = escapeFilePath(apstr,'b')
        ret = unescapeFilePath(ret)
        self.assertEqual(apstr, ret) 

#
#######################
#

if __name__ == '__main__':
    unittest.main()

