"""Check IEEE1003.1-Chap. 4.2.
"""
from __future__ import absolute_import

import unittest
import os,sys

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,getTopFromPathString,unescapeFilePath


#
#######################
#
class UseCase(unittest.TestCase):
    
    def testCase_simple_file_abs(self):
        _s = sys.path[:]
        start = os.path.abspath(os.path.dirname(__file__)+os.path.normpath('/a/b/c'))
        top = os.path.dirname(__file__)
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        myplist = [getTopFromPathString('AppPathSyntax',[os.path.dirname(__file__)+os.sep+start])]
        res = []
        for i in range(len(_res)):
            _p = getPythonPathRel(_res[i],myplist)
            if _p:
                res.append(_p) 
        resx = [
            'file/file_simple/a/b/c',
            'file/file_simple/a/b',
            'file/file_simple/a',
            'file/file_simple',
        ]
        resx = map(os.path.normpath,resx)

        res = map(unescapeFilePath, res)
        resx = map(unescapeFilePath, resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == res
        pass


if __name__ == '__main__':
    unittest.main()
