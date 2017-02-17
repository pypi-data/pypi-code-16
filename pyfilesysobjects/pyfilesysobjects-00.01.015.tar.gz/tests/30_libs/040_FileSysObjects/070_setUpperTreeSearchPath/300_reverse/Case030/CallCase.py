"""Check defaults.
"""
from __future__ import absolute_import

import unittest
import os,sys

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath


#
#######################
#
class CallUnits(unittest.TestCase):
    

    
    

    #
    # Create by object
    #
    def testCase000(self):
        """Check defaults.
        """
        _s = sys.path[:]

        start = os.path.dirname(__file__)+os.sep+'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'+os.sep+'b'+os.sep+'c'+os.sep
        start = os.path.abspath(start)
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'reverse':True}) #@UnusedVariable
        
        mypos = os.path.abspath(os.path.normpath(os.path.dirname(__file__)+"/../../"))   
        res = []
        for i in range(len(_res)):
            pr = getPythonPathRel(_res[i],[mypos])
            if pr:
                res.append(pr)
        resx = [
            '.', 
            '300_reverse', 
            '300_reverse/Case030', 
            '300_reverse/Case030/a', 
            '300_reverse/Case030/a/b', 
            '300_reverse/Case030/a/b/c', 
            '300_reverse/Case030/a/b/c/d', 
            '300_reverse/Case030/a/b/c/d/b', 
            '300_reverse/Case030/a/b/c/d/b/c'
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()
