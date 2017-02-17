"""Check defaults.
"""
from __future__ import absolute_import

import unittest
import os,sys

from filesysobjects.FileSysObjects import setUpperTreeSearchPath,\
    unescapeFilePath


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
        top = None
        res = []
        ret = setUpperTreeSearchPath(start,top,res) #@UnusedVariable
        
        resx = [
            os.path.abspath(os.path.dirname(__file__)),
        ]
        resx = map(os.path.normpath,resx)
        
        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)

        res = map(unescapeFilePath, res)
        resx = map(unescapeFilePath, resx)

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()
