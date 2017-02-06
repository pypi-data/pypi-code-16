"""Create a plist, find a matching relative filepathname in directory tree.

Calling elementary functions.

* **Data**:
  ::
  
    see 'testdata.examples'
  
* **Call**:
  ::

    import testdata
    import filesysobjects.FileSysObjects
      
    s = os.sep
    any_sub_path = os.path.normpath('a/b0/c/d/D.txt')

    spath  = testdata.mypath
    spath += any_sub_path

    # Here an empty list is used for search only. The function adds 
    # entries to the provided list storage, thus e.g. to 'sys.path' too.
    _plist = []

    setUpperTreeSearchPath(spath,os.path.normpath('b/B.txt'), _plist)
    rp = findRelPathInSearchPath(spath,_plist)
    
* **Result**:
  ::

    expected = os.path.normpath(testdata.mypath +s+ 'a/b/B.txt')

"""
from __future__ import absolute_import
from __future__ import print_function

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
from filesysobjects.FileSysObjects import clearPath

#
#######################
#

class CallUnits(unittest.TestCase):
    
    def testCase000(self):
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
        _plist = []


        # 0. build a search path list - if not yet available
        #    adds each directory from spath to its matching 
        #    subnode  "a/b"
        #
        setUpperTreeSearchPath(spath,os.path.normpath('a/b0'), _plist)

        # expected plist
        _plist_ref = [
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c/a'),
            os.path.normpath(testdata.mypath+'/examples/a/b0/c'),
            os.path.normpath(testdata.mypath+'/examples/a/b0'),
        ]
         
        assert _plist_ref == _plist 

        # 1. make it canonical - optional, here just a demo
        _chk_ref = _plist[:]
        _plist.extend(_plist[:]) # duplicate all for demonstration
        assert _plist != _chk_ref
        clearPath(_plist,**{'redundant':True,'shrink':True}) # and clear them immediately
        assert _plist == _chk_ref

        # 2. find the requested entry
        rel = "F"
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/F')
        assert rp_ref == rp 

        rel = "b0/F"
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/F')
        assert rp_ref == rp 

        rel = "b0/c/F"
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/F')
        assert rp_ref == rp 

        rel = "b0/[c]/F"
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/F')
        assert rp_ref == rp 

        rel = "a/b0/[c]/F"
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/F')
        assert rp_ref == rp 

        rel = "a/b?/[c]/F"
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/F')
        assert rp_ref == rp 

        rel = "a/b*/[c]/F"
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/F')
        assert rp_ref == rp 

        rel = "b0/*"
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c')
        assert rp_ref == rp 

        rel = "b0"+os.path.sep+"F*" # bash specific
        rp = findRelPathInSearchPath(rel,_plist,**{'matchidx':1})
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/F')
        #FIXME:
        #assert rp_ref == rp 

        rel = os.path.normpath("c/a/b0/*/F")
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/F')
        assert rp_ref == rp 

        rel = os.path.normpath("c/F")
        rp = findRelPathInSearchPath(rel,_plist)
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c/F')
        assert rp_ref == rp 

        rel = os.path.normpath("c/F")
        rp = findRelPathInSearchPath(rel,_plist,**{'matchidx':1})
        rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/F')
        assert rp_ref == rp 
        
        # 2.a. find the requested entry
        rp = findRelPathInSearchPath("F[0-5]*",_plist)
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/F1')
        assert expected == rp 

        # 2.b. find the requested entry - here as demo with a relative path
        rp = findRelPathInSearchPath("c/*/b0/F[0-5]*",_plist)
        expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/F1')
        assert expected == rp 


#         rel = os.path.normpath("b0/*")
#         rp = findRelPathInSearchPath(rel,_plist,**{'matchidx':2})
#         rp_ref = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/F')
#         assert rp_ref == rp 

    
#
#######################
#

if __name__ == '__main__':
    unittest.main()

