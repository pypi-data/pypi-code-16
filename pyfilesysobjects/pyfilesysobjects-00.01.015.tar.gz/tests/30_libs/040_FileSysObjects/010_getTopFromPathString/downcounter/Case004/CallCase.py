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


class CallUnits(unittest.TestCase):

    def __init__(self,*args,**kargs):
        """Creates search path list
        """
        super(CallUnits,self).__init__(*args,**kargs)    

        self._s = sys.path[:]

        # data
        import testdata
        self.myBase = testdata.mypath+os.sep+"findnodes"

        #
        # prefix from unchanged sys.path
        self.mySysPathPrefixRaw = pysourceinfo.PySourceInfo.getPythonPathFromSysPath(__file__) #@UnusedVariable
        
        self.myTestPath0Rel = os.path.normpath('a/b/c/d/e/f/g')
        self.myTestPath1Rel = self.myTestPath0Rel +os.sep+ self.myTestPath0Rel
        self.myTestPath2Rel = self.myTestPath1Rel +os.sep+ self.myTestPath0Rel
        
        self.myTestPath0 = self.myBase+os.sep+self.myTestPath0Rel #@UnusedVariable
        self.myTestPath1 = self.myBase+os.sep+self.myTestPath1Rel #@UnusedVariable
        self.myTestPath2 = self.myBase+os.sep+self.myTestPath2Rel #@UnusedVariable

    def reset_sys_path(self):
        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(self._s)

    def testCase000(self):

        rpath = 'h'+os.sep
        plist = [self.myTestPath2,]
        
        px = filesysobjects.FileSysObjects.getTopFromPathString(
            rpath,
            plist,
            **{'matchlvlupward':4}
        )

        assert not px
        # assert verifyData(px) 
        pass


#
#######################
#

if __name__ == '__main__':
    unittest.main()

