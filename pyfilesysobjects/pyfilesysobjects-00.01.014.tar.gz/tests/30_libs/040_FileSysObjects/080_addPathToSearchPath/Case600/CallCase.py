from __future__ import absolute_import

import unittest
import os,sys

from filesysobjects.FileSysObjects import setUpperTreeSearchPath,addPathToSearchPath,unescapeFilePath

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
        
        dx = "file://"+os.path.abspath(os.path.dirname(__file__)+os.sep+D)
        addPathToSearchPath(dx, res)

        res = map(os.path.abspath,res)
        res = map(os.path.normpath,res)
        
        resx = [
            os.path.dirname(__file__)+os.sep+D,
            os.path.abspath(os.path.dirname(__file__)),
        ]
        resx = map(os.path.abspath,resx)
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)

        res = map(unescapeFilePath, res)
        resx = map(unescapeFilePath, resx)
        
        self.assertEqual(resx, res)

        pass

if __name__ == '__main__':
    unittest.main()
