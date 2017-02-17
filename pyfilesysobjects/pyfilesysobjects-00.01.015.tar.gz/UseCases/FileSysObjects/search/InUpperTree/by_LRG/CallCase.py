from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.4'
__uuid__='9de52399-7752-4633-9fdc-66c87a9200b8'

__docformat__ = "restructuredtext en"

import unittest
import sys,os
    
import testdata

from filesysobjects.FileSysObjects import setUpperTreeSearchPath,findRelPathInSearchPath
from filesysobjects.FileSysObjects import normpathX
from filesysobjects.FileSysObjects import getTopFromPathString

#
#######################
#

class UseCase(unittest.TestCase):
    def testCase000(self):

        # *** save sys.path ***
        _s = sys.path[:]
        # *********************

        # set search for the call of 'myscript.sh'
        setUpperTreeSearchPath(None,'filesysobjects')

        _start = testdata.mypath + '/findnodes/a/b/c/d/e/f/g/h/a/b/c/d/e/f/g/h/a/b/c/d/e/f/g/h'
        _start = normpathX(_start)
        _top = "a/b/x/y/data"
        _top = normpathX(_top)
        _tlst = []
        
        # 0. get top node within-start/path, this is eventually base on a part of the 
        #    search path, gets the topmost hook by default.
        _top = "a/b/.*/[def]{1}/da*"
        _top = normpathX(_top)
        topX = getTopFromPathString(_top, [_start],**{'hook':True,'pattern':'regnode',})
        topXs = getTopFromPathString(_top, [_start],**{'split':True,'pattern':'regnode',})
        topx = getTopFromPathString(_top, [_start],**{'pattern':'regnode',})
        
        # 1. set the search list 
        t = setUpperTreeSearchPath(_start, topX, _tlst)
        if t:
            # 2. search side branch
            a0 = findRelPathInSearchPath(
                topx,
                _tlst,
                **{'reverse':True,'matchidx':0}
            )


        # *** restore sys.path ***
        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        # ************************
        
        assert a0.endswith(normpathX("findnodes/a/b/c/d/data"))
        assert a0.endswith(os.path.normpath("findnodes/a/b/c/d/data"))
        
        pass

#
#######################
#

if __name__ == '__main__':
    unittest.main()

