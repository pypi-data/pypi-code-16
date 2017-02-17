"""Create a plist, find single-node hooks for side branches in PATH strings.

The first match is used by default, e.g. the branch 'a/new/branch', 
maps the node and extends at 'a/'
  ::

    testdata.mypath+/examples/a/b0/c/a/b0/c
    __________________________a/    
    ____________________________`--new/branch

resulting in:
  ::

    testdata.mypath+'/examples/a/b0/c/a/new/branch'

* **Data**:
  ::
  
    see 'testdata.examples'
  
  refer also to the manual `[filesystem-elements-as-objects] <path_syntax.html#filesystem-elements-as-objects>`_

* **Call**:
  ::

    # 1. search and create a path for a side branch
    sp = os.path.normpath('a/new/branch')
    rp = getTopFromPathString(sp,self._plist)

    # 2. search and create a path for a side branch - use the second plist entry 
    sp = os.path.normpath('c/new/branch')
    rp = getTopFromPathString(sp,self._plist,**{'matchidx':1})

    # 3. search and create a path for a side branch - use the second plist entry + reverse the order        
    sp = os.path.normpath('c/new/branch')
    rp = getTopFromPathString(sp,self._plist,**{'matchidx':1,'reverse':True,})

    # 4. search and create a path for a side branch - match a path entry with and use the second match within a path entry        
    sp = os.path.normpath('c/new/branch')
    rp = getTopFromPathString(sp,self._plist,**{'matchlvl':1,})

    # 5. search and create a path for a side branch UPWARD - match a path entry with and use the second match within a path entry        
    sp = os.path.normpath('c/new/branch')
    rp = getTopFromPathString(sp,self._plist,**{'matchlvlupward':1,})

* **Result**:
  ::

    1. expected = os.path.normpath(testdata.mypath+'/examples/a/new/branch')
    2. expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/new/branch')
    3. expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/new/branch')
    4. expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/new/branch')
    5. expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/new/branch')

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

import os,sys
version = '{0}.{1}'.format(*sys.version_info[:2])
if version in ('2.6',): # pragma: no cover
    import unittest2 as unittest
    from unittest2 import SkipTest
elif version in ('2.7',): # pragma: no cover
    import unittest
    from unittest import SkipTest
else:
    print >>sys.stderr, "ERROR:Requires Python-2.6(.6+) or 2.7"
    sys.exit(1)

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

    # not in 2.6.6
    # @classmethod
    # def setUpClass(self):

    def setUp(self):
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
        assert self._plist_ref == self._plist 


    def testCase001(self):
        """1. search and create a path for a side branch"""
        sp = os.path.normpath('a/new/branch')
        expected = os.path.normpath(testdata.mypath+'/examples/a/new/branch')
        rp = getTopFromPathString(sp,self._plist)
        assert expected == rp 

    def testCase002(self):
        """2. search and create a path for a side branch - use the second plist entry""" 
        sp = os.path.normpath('b0/c/new/branch')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/new/branch')
        rp = getTopFromPathString(sp,self._plist,**{'matchidx':1})
        assert expected == rp 

    def testCase003(self):
        """3. search and create a path for a side branch - use the second plist entry + reverse the order"""        
        sp = os.path.normpath('b0/c/new/branch')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/new/branch')
        rp = getTopFromPathString(sp,self._plist,**{'matchidx':1,'reverse':True,})
        self.assertEqual(expected,rp) 

    def testCase004(self):
        """4. search and create a path for a side branch - match a path entry with and use the second match within a path entry"""        
        sp = os.path.normpath('b0/c/new/branch')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/new/branch')
        rp = getTopFromPathString(sp,self._plist,**{'matchlvl':1,})
        self.assertEqual(expected,rp) 

    def testCase005(self):
        """5. search and create a path for a side branch UPWARD - match a path entry with and use the second match within a path entry"""        
        sp = os.path.normpath('c/new/branch')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/new/branch')
        rp = getTopFromPathString(sp,self._plist,**{'matchlvlupward':1,})
        assert expected == rp 

#
#######################
#

if __name__ == '__main__':
    unittest.main()

