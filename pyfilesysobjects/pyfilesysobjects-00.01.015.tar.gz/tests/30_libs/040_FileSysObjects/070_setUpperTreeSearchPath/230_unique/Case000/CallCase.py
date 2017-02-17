from __future__ import absolute_import

import unittest
import os,sys

from filesysobjects.FileSysObjects import setUpperTreeSearchPath


#
#######################
#
class CallUnits(unittest.TestCase):
    

    
    

    #
    # Create by object
    #
    def testCase000(self):
        _s = sys.path[:]

        A = os.path.normpath('a/A.txt')         #@UnusedVariable
        B = os.path.normpath('a/b/B.txt')       #@UnusedVariable
        C = os.path.normpath('a/b/c/C.txt')     #@UnusedVariable
        D = os.path.normpath('a/b/c/d/D.txt')   #@UnusedVariable

        start = os.path.abspath(os.path.dirname(os.path.dirname(__file__)+os.sep+D))
        top = os.path.dirname(__file__)
        res_ = [
            os.path.abspath(os.path.dirname(__file__)),
            os.path.dirname(os.path.dirname(__file__)+os.sep+C),
            os.path.dirname(os.path.dirname(__file__)+os.sep+A),
        ]
        res = map(os.path.abspath,res_)
        res = map(os.path.normpath,res)
        ret = setUpperTreeSearchPath(start,top,res,**{'unique':True}) #@UnusedVariable

        resx_ = [
            os.path.dirname(os.path.dirname(__file__)+os.sep+D),
            os.path.dirname(os.path.dirname(__file__)+os.sep+B),
            os.path.abspath(os.path.dirname(__file__)),
            os.path.dirname(os.path.dirname(__file__)+os.sep+C),
            os.path.dirname(os.path.dirname(__file__)+os.sep+A),
        ]
        resx = map(os.path.abspath,resx_)
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()
