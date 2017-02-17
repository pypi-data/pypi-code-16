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

        p0 = os.path.normpath('a0/b')
        p1 = os.path.normpath('a0/b/a1/b')
        p2 = os.path.normpath('a0/b/a1/b/a2/b')
        p3 = os.path.normpath('a0/b/a1/b/a2/b/a3/b')

        rpath = os.path.normpath('b/')
        plistRaw = [
            p3,
        ]
        plist = plistRaw[:]
        filesysobjects.FileSysObjects.clearPath(plist,**{'redundant':True,'shrink':True,'split':True}) # here just a demo
        plistRef = [
            p3,
        ]        
        assert plist == plistRef

        kargs = {'matchlvl':1}
        px = []
        for ix in filesysobjects.FileSysObjects.getTopFromPathStringIter(rpath, plist,**kargs):
            px.append(os.path.normpath(ix))
        
        pxn = [
            p1,
        ]

        assert px == pxn 
        pass


#
#######################
#

if __name__ == '__main__':
    unittest.main()

