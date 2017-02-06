"""Check defaults.
"""
from __future__ import absolute_import

import unittest
import os,sys

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,\
    FileSysObjectsException


#
#######################
#
class CallUnits(unittest.TestCase):

    def testCase000(self):
        _s = sys.path[:]
        start = os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        start = os.path.abspath(start)
        
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':0,'relonly':True,'ias':True}) #@UnusedVariable
        
        forDebugOnly = sys.path #@UnusedVariable
        
#        res = []
#         for i in range(len(_res)):
#             res.append(getPythonPathRel(_res[i]))
            
        resx = [
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c/d/tests/b/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c/d/tests/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c/d/tests', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c/d', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b/tests', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests/a', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a/tests', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020/a', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly/Case020', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/240_relonly', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath', 
            '30_libs/040_FileSysObjects', 
            '30_libs'
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == _res
        pass

    def testCase001(self):
        _s = sys.path[:]
        start = os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        start = os.path.abspath(start)
        
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':1,'relonly':True,'ias':True}) #@UnusedVariable
        
        forDebugOnly = sys.path #@UnusedVariable
        
        resx = [
            'a/b/tests/c/d/tests/b/c', 
            'a/b/tests/c/d/tests/b', 
            'a/b/tests/c/d/tests', 
            'a/b/tests/c/d', 
            'a/b/tests/c', 
            'a/b/tests', 
            'a/b', 
            'a'
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
                
        assert resx == _res
        pass

    def testCase002(self):
        _s = sys.path[:]
        start = os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        start = os.path.abspath(start)
        
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':2,'relonly':True,'ias':True}) #@UnusedVariable
        
        forDebugOnly = sys.path #@UnusedVariable
        
        resx = [
            'c/d/tests/b/c', 
            'c/d/tests/b', 
            'c/d/tests', 
            'c/d', 
            'c'
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
                
        assert resx == _res
        pass

    def testCase003(self):
        _s = sys.path[:]
        start = os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c'
        start = os.path.abspath(start)
        
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':3,'relonly':True,'ias':True}) #@UnusedVariable
        
        forDebugOnly = sys.path #@UnusedVariable
        
        resx = [
            'b/c', 
            'b'
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
                
        assert resx == _res
        pass

if __name__ == '__main__':
    unittest.main()
