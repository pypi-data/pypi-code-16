"""Create a plist, find side branches with slices of multi-node hooks.

E.g. the branch 'a/b0/F[0-7]*', which maps the slice 'a/b0' and extends at 'a/b0' by 'glob'
  ::

    testdata.mypath+/examples/a/b0/c/a/b0/c
    __________________________a/b0/    
    ______________________________`--F[0-7]*

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
    sp = os.path.normpath('c/a/new/branch')
    rp = getTopFromPathString(sp,self._plist)

    # 2. search and create a path for a side branch - use the second plist entry 
    sp = os.path.normpath('b0/c/new/branch')
    rp = getTopFromPathString(sp,self._plist,**{'matchidx':1})

    # 3. search and create a path for a side branch - use the second plist entry + reverse the order        
    sp = os.path.normpath('b0/c/new/branch')
    rp = getTopFromPathString(sp,self._plist,**{'matchidx':1,'reverse':True,})

    # 4. search and create a path for a side branch - match a path entry with and use the second match within a path entry        
    sp = os.path.normpath('b0/c/new/branch')
    rp = getTopFromPathString(sp,self._plist,**{'matchlvl':1,})

    # 5. search and create a path for a side branch UPWARD - match a path entry with and use the second match within a path entry        
    sp = os.path.normpath('b0/c/new/branch')
    rp = getTopFromPathString(sp,self._plist,**{'matchlvlupward':1,})

* **Result**:
  ::

    1. expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/new/branch')
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
        self._plist = []


        # 0. build a search path list - if not yet available
        #    adds each directory from spath to its matching 
        #    subnode  "a/b"
        #
        setUpperTreeSearchPath(spath,os.path.normpath('examples/a'), self._plist)
        self._plist_ref = [ # expected plist
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0'),
            os.path.normpath(testdata.mypath+'/examples/a'),
        ]
        assert self._plist_ref == self._plist 


        _tmplist = []
        _tmp_start = testdata.mypath + os.path.normpath('/examples/a/b0/a/b0/c/F')
        setUpperTreeSearchPath(_tmp_start,os.path.normpath('examples/a'), _tmplist)
        _tmplist_ref = [ # expected plist
            os.path.normpath(testdata.mypath+'/examples/a/b0/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/a/b0'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b0'),
            os.path.normpath(testdata.mypath+'/examples/a'),
        ]
        assert _tmplist_ref == _tmplist
        self._plist.extend(_tmplist) 
 
        _tmplist = []
        _tmp_start = testdata.mypath + os.path.normpath('/examples/a/b2/a/b0/c/F')
        setUpperTreeSearchPath(_tmp_start,os.path.normpath('examples/a'), _tmplist)
        _tmplist_ref = [ # expected plist
            os.path.normpath(testdata.mypath+'/examples/a/b2/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b2/a/b0'),
            os.path.normpath(testdata.mypath+'/examples/a/b2/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b2'),
            os.path.normpath(testdata.mypath+'/examples/a'),
        ]
        assert _tmplist_ref == _tmplist
        self._plist.extend(_tmplist) 

        _tmplist = []
        _tmp_start = testdata.mypath + os.path.normpath('/examples/a/b1/c/F')
        setUpperTreeSearchPath(_tmp_start,os.path.normpath('examples/a'), _tmplist)
        _tmplist_ref = [ # expected plist
            os.path.normpath(testdata.mypath+'/examples/a/b1/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b1'),
            os.path.normpath(testdata.mypath+'/examples/a'),
        ]
        assert _tmplist_ref == _tmplist
        self._plist.extend(_tmplist) 

    def testCase003(self):
        """3. search and create a path for a side branch - use the second plist entry + reverse the order"""        
        import testdata

#TODO:
#        sp  = testdata.mypath+os.path.normpath('/examples/[a-z]/b[02]/[a]:')
#        sp += os.pathsep+testdata.mypath+os.path.normpath('/examples/[a-z]/b[02]/[F]:')

#        sp = testdata.mypath+os.path.normpath('/examples/[a-z]/b[02]/[aF]')

        sp = os.path.normpath('examples/[a-z]/b[02]/[ac]')
        a = []
        for it in getTopFromPathStringIter(sp,self._plist,**{'pattern':'regnode','patternlvl':3}):
            a.append(it)

        aref = [
            os.path.normpath(testdata.mypath+'/examples/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c'), 
            os.path.normpath(testdata.mypath+'/examples/a/b0/[ac]'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/[ac]'),
            os.path.normpath(testdata.mypath+'/examples/a/b2/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b2/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b2/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b2/[ac]'),
        ]
        self.assertEqual(a, aref) 

#         import glob
#         gx = glob.glob(rp)
#         gref = [
#             os.path.normpath(testdata.mypath+'/examples/a/b2/a/b0/F'),
#             os.path.normpath(testdata.mypath+'/examples/a/b0/a/b0/F'),
#         ]
#         assert gref.sort() == gx.sort()

    def testCase003a(self):
        """3. search and create a path for a side branch - use the second plist entry + reverse the order"""        
        import testdata

#        sp = testdata.mypath+os.path.normpath('/examples/.*/[a-z]*/*/*/F')
#        sp = testdata.mypath+os.path.normpath('/examples/.*/[a-z]*/*/*')
#        sp = os.path.normpath('examples/.*/[a-z][0-6]/*/*/F')
        sp = os.path.normpath('examples/.*/[a-z]*/*/*/F')
        expected = os.path.normpath(testdata.mypath+'/examples/a/[a-z]*/*/*/F')
        rp = getTopFromPathString(sp,self._plist,**{'pattern':'regnode','matchidx':1})
        assert expected == rp 

        import glob
        gx = glob.glob(rp)
        gref = [
            os.path.normpath(testdata.mypath+'/examples/a/b2/a/b0/F'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/a/b0/F'),
        ]
        assert gref.sort() == gx.sort()

    def testCase003b(self):
        """3. search and create a path for a side branch - use the second plist entry + reverse the order"""        
        import testdata

        sp = os.path.normpath('examples/.*/.*0/.*/*')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/*')
        rp = getTopFromPathString(sp,self._plist,**{'pattern':'regnode','matchidx':1})
        assert expected == rp 

        import glob
        gx = glob.glob(rp)
        gref = [
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/__init__.py'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/F'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a'),
        ]
        assert gref.sort() == gx.sort()

    def testCase003c(self):
        """3. search and create a path for a side branch - use the second plist entry + reverse the order"""        
        import testdata

        sp = os.path.normpath('examples/.*/.*/.*/*')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/*')
        rp = getTopFromPathString(sp,self._plist,**{'pattern':'regnode','matchidx':1})
        assert expected == rp 

        import glob
        gx = glob.glob(rp)
        gref = [
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/__init__.py'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/F'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a'),
        ]
        assert gref.sort() == gx.sort()

    def testCase003d(self):
        """3. search and create a path for a side branch - use the second plist entry + reverse the order"""        
        import testdata

        sp = os.path.normpath('/examples/.*/.*/.*/*')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/*')
        rp = getTopFromPathString(sp,self._plist,**{'pattern':'regnode','matchidx':1})
        assert expected == rp 

        import glob
        gx = glob.glob(rp)
        gref = [
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/__init__.py'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/F'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a'),
        ]
        assert gref.sort() == gx.sort()

    def testCase003e(self):
        """3. search and create a path for a side branch - use the second plist entry + reverse the order"""        
        import testdata

        sp = testdata.mypath+os.path.normpath('/examples/.*/.*/.*/*')
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/*')
        rp = getTopFromPathString(sp,self._plist,**{'pattern':'regnode','matchidx':1})
        assert expected == rp 

        import glob
        gx = glob.glob(rp)
        gref = [
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/__init__.py'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/F'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a'),
        ]
        assert gref.sort() == gx.sort()


#
#######################
#

if __name__ == '__main__':
    unittest.main()

