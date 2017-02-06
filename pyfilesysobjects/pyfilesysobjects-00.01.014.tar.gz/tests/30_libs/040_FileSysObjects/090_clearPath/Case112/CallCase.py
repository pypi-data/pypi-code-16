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
            os.path.normpath("/a0/b/c"),
            os.path.normpath("/a1/b/c"+os.pathsep+"/a11/b"+os.pathsep+"/a1/b/c"+os.pathsep+"/a11/b"+os.pathsep+"/a1/b/c"+os.pathsep+"/a11/b"+os.pathsep+"/a1/b/c"+os.pathsep+"/a11/b"),
            os.path.normpath("/a2/b/c"),
            os.path.normpath("/a0/b/c"),
            os.path.normpath("/a1/b/c"+os.pathsep+"/a0/b/c"+os.pathsep+"/a11/b"),
            os.path.normpath("/a2/b/c"),
        ]        
        plist = plistRaw[:]
        
        filesysobjects.FileSysObjects.clearPath(plist,**{'redundant':True,'shrink':True,'split':True,}) # here just a demo
        plistRef = [
            os.path.normpath('/a0/b/c'), 
            os.path.normpath('/a1/b/c'), 
            os.path.normpath('/a11/b'), 
            os.path.normpath('/a2/b/c')
        ]

        assert plist == plistRef

        pass


#
#######################
#

if __name__ == '__main__':
    unittest.main()

