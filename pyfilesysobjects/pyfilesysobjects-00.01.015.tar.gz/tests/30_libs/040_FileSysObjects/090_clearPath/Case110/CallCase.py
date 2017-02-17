from __future__ import absolute_import
from __future__ import print_function
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
    
    def testCase000(self):

        plistRaw = [
            "/a0/b/c",
            "/a1/b/c:/a11/b",
            "/a2/b/c",
            "/a0/b/c", 
            "/a1/b/c:/a11/b",
            "/a2/b/c",
        ]        
        plist = map(os.path.normpath, plistRaw)
        
        filesysobjects.FileSysObjects.clearPath(plist,**{'redundant':True,'shrink':True,}) # here just a demo
        plistRef = [
            '/a0/b/c',
            '/a1/b/c:/a11/b',
            '/a2/b/c'
        ]
        plistRef = map(os.path.normpath, plistRef)

        assert plist == plistRef

        pass


#
#######################
#

if __name__ == '__main__':
    unittest.main()

