from __future__ import absolute_import

import unittest
import os,sys

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,getTopFromPathString,unescapeFilePath


#
#######################
#
class UseCase(unittest.TestCase):
    
    def testCase_file_path(self):
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
            'ieee1003/generic_app_path/a/b/c', 
            'ieee1003/generic_app_path/a/b', 
            'ieee1003/generic_app_path/a',
            'ieee1003/generic_app_path',
        ]        
        resx = map(os.path.normpath,resx)

        res = map(unescapeFilePath, res)
        resx = map(unescapeFilePath, resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == res
        pass

    def app_path(self):
        _s = sys.path[:]
        start = os.path.normpath('a/b/c')
        top = os.path.dirname(__file__)
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        myplist = [getTopFromPathString('tests',[os.path.dirname(__file__)+os.sep+start])]
        res = []
        for i in range(len(_res)):
            _p = getPythonPathRel(_res[i],myplist)
            if _p:
                res.append(_p) 
        resx = [
            'generic_app_path/a/b/c', 
            'generic_app_path/a/b', 
            'generic_app_path/a',
            'generic_app_path',
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
