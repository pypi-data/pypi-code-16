from __future__ import absolute_import

import os,sys
import unittest

from filesysobjects.FileSysObjects import setUpperTreeSearchPath,addPathToSearchPath
import testdata


#
#######################
#
class CallUnits(unittest.TestCase):

    def testCase000(self):
        _s = sys.path[:]

        A = os.path.normpath('a/A.txt')         #@UnusedVariable
        B = os.path.normpath('a/b/B.txt')       #@UnusedVariable
        C = os.path.normpath('a/b/c/C.txt')     #@UnusedVariable
        D = os.path.normpath('a/b/c/d/D.txt')   #@UnusedVariable
 
        start = os.path.abspath(os.path.dirname(__file__))
        top = start
        res = []
        ret = setUpperTreeSearchPath(start,top,res) #@UnusedVariable
        dx = "file://"+os.path.abspath(testdata.mypath+os.sep+D)
        addPathToSearchPath( dx, res)
        res = map(os.path.normpath,res)

        resx = [
            testdata.mypath+os.sep+D,
            os.path.dirname(__file__),
        ]
        resx = map(os.path.normpath,resx)
        resx = map(os.path.abspath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)

        self.assertEqual(resx, res)
        pass

if __name__ == '__main__':
    unittest.main()
