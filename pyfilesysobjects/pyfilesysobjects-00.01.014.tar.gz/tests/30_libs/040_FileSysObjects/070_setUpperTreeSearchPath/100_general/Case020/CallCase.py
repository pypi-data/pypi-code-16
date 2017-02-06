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

        start = os.path.abspath(os.path.dirname(__file__))
        top = 'tests'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
        
        mypos = os.path.abspath(os.path.normpath(os.path.dirname(__file__)+"/../../"))   
        res = []
        for i in range(len(_res)):
            pr = getPythonPathRel(_res[i],[mypos])
            if pr:
                res.append(pr)
        resx = [
            '100_general/Case020', '100_general', '.'
        ]        
        resx = map(os.path.normpath, resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()
