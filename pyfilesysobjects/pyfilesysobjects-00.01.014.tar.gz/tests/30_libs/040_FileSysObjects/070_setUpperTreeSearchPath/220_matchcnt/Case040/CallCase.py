"""Check defaults.
"""
from __future__ import absolute_import

import unittest
import os,sys

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,\
    FileSysObjectsException,getTopFromPathString


#
#######################
#
class CallUnits(unittest.TestCase):

    def testCase000(self):
        _s = sys.path[:]
        start = os.path.normpath(os.path.dirname(__file__)+os.sep+'a/tests//////a/b/tests//c////////d/tests/b///c')
        start = os.path.abspath(start)
        
        top = os.path.normpath('tests///')
        top = getTopFromPathString(top,[start])

        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':0,'ias':True}) #@UnusedVariable
                
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],[top]))
            
        resx = [
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b/c',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d/tests', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c/d', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b/tests', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests/a', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a/tests', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040/a', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt/Case040', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/220_matchcnt', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath', 
            '30_libs/040_FileSysObjects', 
            '30_libs', 
            '', 
        ]
        resx = map(os.path.normpath, resx)
        res = map(os.path.normpath, res)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
                
        assert resx == res
        pass

    def testCase000r(self):
        _s = sys.path[:]

        start = os.path.normpath(os.path.dirname(__file__)+os.sep+'a/tests//////a/b/tests//c////////d/tests/b///c')
        start = os.path.abspath(start)

        top = os.path.normpath('tests///')
        top = getTopFromPathString(top, [start]) #@UnusedVariable


        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':0,'reverse':True,'ias':True}) #@UnusedVariable

        mypos = os.path.abspath(os.path.normpath(os.path.dirname(__file__)+"/../"))   
        res = []
        for i in range(len(_res)):
            pr = getPythonPathRel(_res[i],[mypos])
            if pr:
                res.append(pr)
        
        resx = [
            '.', 
            'Case040', 
            'Case040/a', 
            'Case040/a/tests', 
            'Case040/a/tests/a', 
            'Case040/a/tests/a/b', 
            'Case040/a/tests/a/b/tests', 
            'Case040/a/tests/a/b/tests/c', 
            'Case040/a/tests/a/b/tests/c/d', 
            'Case040/a/tests/a/b/tests/c/d/tests', 
            'Case040/a/tests/a/b/tests/c/d/tests/b', 
            'Case040/a/tests/a/b/tests/c/d/tests/b/c'
        ]

        res = map(os.path.normpath, res)
        resx = map(os.path.normpath, resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)

        self.assertEqual(resx ,res) 
        pass

    def testCase001(self):
        _s = sys.path[:]
        start = os.path.normpath(os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c')
        start = os.path.abspath(start)
        
        top = os.path.normpath('tests')
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':1,'reverse':True,'ias':True}) #@UnusedVariable
        
        mypos = os.path.abspath(os.path.normpath(os.path.dirname(__file__)+"/../"))   
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],[mypos]))
            
        resx = [
            'Case040/a/tests', 
            'Case040/a/tests/a', 
            'Case040/a/tests/a/b',
            'Case040/a/tests/a/b/tests', 
            'Case040/a/tests/a/b/tests/c', 
            'Case040/a/tests/a/b/tests/c/d', 
            'Case040/a/tests/a/b/tests/c/d/tests', 
            'Case040/a/tests/a/b/tests/c/d/tests/b', 
            'Case040/a/tests/a/b/tests/c/d/tests/b/c'
        ]

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        resx = map(os.path.abspath, resx)
        res = map(os.path.abspath, res)

        assert resx == res
        pass

    def testCase002(self):
        _s = sys.path[:]
        start = os.path.normpath(os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c')
        start = os.path.abspath(start)
        
        top = os.path.normpath('tests')
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':2,'reverse':True,'ias':True}) #@UnusedVariable

        mypos = os.path.abspath(os.path.normpath(os.path.dirname(__file__)+"/../"))   
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],[mypos]))
            
        resx = [
            'Case040/a/tests/a/b/tests', 
            'Case040/a/tests/a/b/tests/c', 
            'Case040/a/tests/a/b/tests/c/d', 
            'Case040/a/tests/a/b/tests/c/d/tests', 
            'Case040/a/tests/a/b/tests/c/d/tests/b', 
            'Case040/a/tests/a/b/tests/c/d/tests/b/c'
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        resx = map(os.path.abspath, resx)
        res = map(os.path.abspath, res)
        
        assert resx == res
        pass


    def testCase005(self):
        _s = sys.path[:]
        start = os.path.normpath(os.path.dirname(__file__)+os.sep+'a/tests/a/b/tests/c/d/tests/b/c')
        start = os.path.abspath(start)
        
        top = os.path.normpath('tests')
        _res = []
        try:
            ret = setUpperTreeSearchPath(start,top,_res,**{'matchlvl':5,'ias':True}) #@UnusedVariable
        except FileSysObjectsException as e: #@UnusedVariable
            pass
        else:
            assert False
        pass

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        


if __name__ == '__main__':
    unittest.main()
