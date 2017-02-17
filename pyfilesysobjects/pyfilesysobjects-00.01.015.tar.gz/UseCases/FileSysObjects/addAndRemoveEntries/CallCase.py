"""Create a plist, find a matching relative filepathname in directory tree.

Calling elementary functions.

* **Data**:
  ::
  
    see 'testdata.examples'
  
  refer also to the manual `[filesystem-elements-as-objects] <path_syntax.html#filesystem-elements-as-objects>`_

* **Call**:
  ::

    import testdata
    import filesysobjects.FileSysObjects
      
    # start of upward search - file is converted into it's containing directory node
    s = os.sep
    any_sub_path = os.path.normpath('examples/a/b0/c/a/b0/c/F')
    spath  = testdata.mypath
    spath += any_sub_path

    # Here an empty list is used for search only. The function adds 
    # entries to the provided list storage, thus e.g. to 'sys.path' too.
    _plist = []

    # 0. build a search path list - if not yet available
    #    adds each directory from spath to its matching 
    #    subnode  "a/b"
    #
    setUpperTreeSearchPath(spath,os.path.normpath('b/B.txt'), _plist)
    rp = findRelPathInSearchPath(spath,_plist)


    _addp = _plist_ref[-1]

    # 1. append an item       
    _px = addPathToSearchPath(_addp, _plist,**{'append':True})

    # 2. remove the item
    delPathFromSearchPath(_addp, _plist)

* **Result**:
  ::

    expected = os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/F1')

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

import testdata

from filesysobjects.FileSysObjects import addPathToSearchPath
from filesysobjects.FileSysObjects import delPathFromSearchPath
from filesysobjects.FileSysObjects import setUpperTreeSearchPath
from filesysobjects.FileSysObjects import findRelPathInSearchPath
from filesysobjects.FileSysObjects import clearPath


#
#######################
#
_plist_ref = [ 
    os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0/c'),
    os.path.normpath(testdata.mypath+'/examples/a/b0/c/a/b0'),
    os.path.normpath(testdata.mypath+'/examples/a/b0/c/a'),
    os.path.normpath(testdata.mypath+'/examples/a/b0/c'),
    os.path.normpath(testdata.mypath+'/examples/a/b0'),
    os.path.normpath(testdata.mypath+'/examples/a'),
]
"""reference data for usecase"""


# start of upward search - file is converted into it's containing directory node
any_sub_path = os.path.normpath('examples/a/b0/c/a/b0/c/F')

spath  = testdata.mypath
spath += os.sep+ any_sub_path
# check environment
assert os.path.exists(spath)

_plist = []
"""test data for incremental update by usecases"""

# 0. build a search path list - if not yet available
#    adds each directory from spath to its matching 
#    subnode  "a/b"
#
setUpperTreeSearchPath(spath,os.path.normpath('a/b0'), _plist)

# validate initial state
assert _plist_ref[:-1] == _plist 

class UseCase(unittest.TestCase):
    def __init__(self,*args,**kargs):
        """Setup reference data as singleton
        """
        super(UseCase,self).__init__(*args,**kargs)

        self._plist = _plist
        self._plist_ref = _plist_ref

        pass

    def test_UseCase000_append(self):
        """1. append an item"""       
        _addp = self._plist_ref[-1]
        _px = addPathToSearchPath(_addp, self._plist,**{'append':True})
        assert _px == len(self._plist_ref)-1 # here just a demo
        assert self._plist_ref == self._plist 
        pass

    def test_UseCase010_prepend_same_again(self):
        """2. append same item again - with success"""
        _addp = self._plist_ref[-1]
        _px = addPathToSearchPath(_addp, self._plist,**{'prepend':True,'redundant':True})
        assert len(self._plist) == len(self._plist_ref)+1 # here just a demo
        assert self._plist_ref == self._plist[1:] 
        assert self._plist[0] == _addp 

    def test_UseCase020_append_try_same_again_nonredundant(self):
        """3. try to add same item again - with failure"""
        _addp = self._plist_ref[-1]
        _plist_in = self._plist[:]
        _px = addPathToSearchPath(_addp, self._plist,**{'prepend':True,'redundant':False})
        assert _px == None
        self.assertEqual(_plist_in, self._plist)

    def test_UseCase021_append_try_same_again_nonredundant(self):
        """3. try to add same item again - with failure"""
        _addp = self._plist_ref[-1]
        _plist_in = self._plist[:]
        _px = addPathToSearchPath(_addp, self._plist,**{'append':True,'redundant':False})
        assert _px == None
        self.assertEqual(_plist_in, self._plist)

    def test_UseCase030_prepend_same_again_checkreal(self):
        """4. prepend same item again - with checkreal"""
        _addp = self._plist_ref[-1]
        _plist_in = self._plist[:]
        _plist_in.insert(0,os.path.realpath(_addp))
        _px = addPathToSearchPath(_addp, self._plist,**{'prepend':True,'redundant':True,'checkreal':True,})
        assert _px == 0
        assert _plist_in == self._plist 

    def test_UseCase040_delete_same(self):
        """5. remove the item"""
        _addp = self._plist_ref[-1]
        delPathFromSearchPath(_addp, self._plist)
        assert self._plist_ref[:-1] == self._plist 


    
#
#######################
#

if __name__ == '__main__':
    unittest.main()

