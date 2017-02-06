from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.1.4'
__uuid__='9de52399-7752-4633-9fdc-66c87a9200b8'

__docformat__ = "restructuredtext en"

import unittest
import sys
    
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

        _tlst = []

        _start = testdata.mypath + '/findnodes/a/b/c/d/e/f/g/h/a/b/c/d/e/f/g/h/a/b/c/d/e/f/g/h'
        _start = normpathX(_start)
        
        # 0. get top node by regular expression
        _top = "a/b/[a-z]+/.*/data"
        _top = normpathX(_top)
        topX = getTopFromPathString(_top, [_start],**{'hook':True, 'pattern':'regnode',})
        topx = getTopFromPathString(_top, [_start],**{'pattern':'regnode',})
        
        _top = "a/b/.*/[def]{1}/data"
        _top = normpathX(_top)
        topY = getTopFromPathString(_top, [_start],**{'hook':True,'pattern':'regnode',})
        topy = getTopFromPathString(_top, [_start],**{'pattern':'regnode',})

        # *** restore sys.path ***
        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        # ************************
        
        assert topX == topY
        pass

#
#######################
#

if __name__ == '__main__':
    unittest.main()

