"""Create a plist, find side branches with single and multi-node hooks.

* **Data**:
  ::
  
    see 'testdata.examples'
  
  refer also to the manual `[filesystem-elements-as-objects] <path_syntax.html#filesystem-elements-as-objects>`_

* **Call**:
  ::

    # 1. search and create a path for a side branch - single node hook
    sp = os.path.normpath('a/new/branch')
    rp = getTopFromPathString(sp,self._plist)

    # 2. search and create a path for a side branch by a multipoint hook as a slice
    sp = os.path.normpath('c/a/new/branch')
    rp = getTopFromPathString(sp,self._plist)


* **Result**:
  ::

    1. expected = os.path.normpath(testdata.mypath+'/examples/a/new/branch')
    2. expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/new/branch')

"""
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
from filesysobjects.FileSysObjects import getTopFromPathString

import testdata

#
#######################
#

class UseCase(unittest.TestCase):
    
    def __init__(self,*args,**kargs):
        """Initialize common refence and data"""
        
        super(UseCase,self).__init__(*args,**kargs)
        
        _s = sys.path[:]
        s = os.sep
        
        # start of upward search - file is converted into it's containing directory node
        any_sub_path = os.path.normpath('examples/a/b0/c/a/b0/c/F')
        spath  = testdata.mypath
        spath += s+ any_sub_path

        # check environment
        assert os.path.exists(spath)
                
        # store new search list, here without required sys.path
        self._plist = []


        # 0. build a search path list - if not yet available
        #    adds each directory from spath to its matching 
        #    subnode  "a/b"
        #
        setUpperTreeSearchPath(spath,os.path.normpath('a/b0'), self._plist)
        self._plist_ref = [ # expected plist
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0'),
        ]
        self.assertEqual(self._plist_ref, self._plist) 


    def testCase001(self):
        """1. search and create a path for a side branch by a single point hook"""
        sp = os.path.normpath('a/new/branch')
        expected = os.path.normpath(testdata.mypath+'/examples/a/new/branch')
        rp = getTopFromPathString(sp,self._plist)
        self.assertEqual(expected, rp) 

    def testCase002(self):
        """1. search and create a path for a side branch by a multipoint hook as a slice"""
        sp = os.path.normpath('b0/c/a/new/branch')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/new/branch')
        rp = getTopFromPathString(sp,self._plist)
        self.assertEqual(expected, rp) 


#
#######################
#

if __name__ == '__main__':
    unittest.main()

