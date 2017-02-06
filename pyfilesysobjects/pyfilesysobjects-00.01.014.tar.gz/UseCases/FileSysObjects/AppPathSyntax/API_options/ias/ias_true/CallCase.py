from __future__ import absolute_import

import unittest
import os,sys

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,splitAppPrefix,getAppPrefixLocalPath,getTopFromPathString


#
#######################
#
class UseCase(unittest.TestCase):
    
    def testCase_IAS_True(self):
        _s = sys.path[:]
        
        start0 = os.path.abspath(os.path.dirname(__file__)+os.sep+os.path.normpath('/a/b/c'))
        d,p = os.path.splitdrive(start0) #@UnusedVariable
        start1 = os.sep + p #@UnusedVariable
    
        # normalize
        _start_elems = splitAppPrefix(start0,**{'ias':True})
        start= getAppPrefixLocalPath(_start_elems)

        assert start0 == start
        
        top = 'AppPathSyntax/'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'ias':True}) #@UnusedVariable

        myplist = [getTopFromPathString('AppPathSyntax',[start])]
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],myplist)) 
        resx = [
             'API_options/ias/ias_true/a/b/c',
             'API_options/ias/ias_true/a/b',
             'API_options/ias/ias_true/a',
             'API_options/ias/ias_true',
             'API_options/ias',
             'API_options',
             '.',
        ]        
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == res
        pass



if __name__ == '__main__':
    unittest.main()
