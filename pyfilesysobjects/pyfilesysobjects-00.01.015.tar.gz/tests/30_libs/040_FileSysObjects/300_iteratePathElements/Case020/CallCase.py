from __future__ import absolute_import
from __future__ import print_function
import filesysobjects

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,sys

from filesysobjects.FileSysObjects import setUpperTreeSearchPath
from filesysobjects.FileSysObjects import findRelPathInSearchPath
from filesysobjects.FileSysObjects import getTopFromPathString,getTopFromPathStringIter

#
#######################
#

class CallUnits(unittest.TestCase):
    
    def __init__(self,*args,**kargs):
        """Initialize common refence and data"""
        
        super(CallUnits,self).__init__(*args,**kargs)
        
        _s = sys.path[:]

        import testdata
          
        s = os.sep
        
        # start of upward search - file is converted into it's containing directory node
        any_sub_path = os.path.normpath('examples/a/b0/c/a/b0/c/F')
        spath  = testdata.mypath
        spath += s+ any_sub_path

        # check environment
        assert os.path.exists(spath)
                
        # store new search list, here without required sys.path
        self._plist = [ # expected plist
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b1/a/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b2/c/a/b0/c'),
        ]



    def testCase010(self):
        import testdata

        sp = os.path.normpath('examples/[a-z]/b[02]/[ac]')
        #expected = os.path.normpath(testdata.mypath+'/examples/a/*/*/*/F')
        a = 0
        for it in getTopFromPathStringIter(sp,self._plist,**{'pattern':'regnode','patternlvl':3}):
            a += 1

#
#######################
#

if __name__ == '__main__':
    unittest.main()

