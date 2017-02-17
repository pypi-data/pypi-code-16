"""Find a matching relative filepathname in upper directory tree.

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

class UseCase(unittest.TestCase):
    
    def testCase000(self):
        _s = sys.path[:]

        import testdata
          
        s = os.sep
        
        # start of upward search - file is converted into it's containing directory node
        any_sub_path = os.path.normpath('a/b/c/')
        spath  = testdata.mypath
        spath += s+ any_sub_path
        
        # store new search list, here without required sys.path
        _plist = []


        # 0. build a search path list - if not yet available
        #    adds each directory from spath to its matching 
        #    subnode  "a/b"
        #
        setUpperTreeSearchPath(spath,os.path.normpath('a/b'), _plist)
        
        # 1. make it canonical - optional
        clearPath(_plist)
        
        # 2. find the requested entry
        rp = findRelPathInSearchPath(spath,_plist)

        expected = os.path.normpath(testdata.mypath +s+ 'a/b/c')
        assert rp == expected
    
#
#######################
#

if __name__ == '__main__':
    unittest.main()

