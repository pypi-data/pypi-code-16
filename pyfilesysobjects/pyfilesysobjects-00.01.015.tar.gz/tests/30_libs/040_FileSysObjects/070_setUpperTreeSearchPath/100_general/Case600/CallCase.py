"""Check error condition.
"""
from __future__ import absolute_import

import unittest
import os,sys

from filesysobjects.FileSysObjects import setUpperTreeSearchPath,FileSysObjectsException


#
#######################
#
class CallUnits(unittest.TestCase):
    

    
    

    #
    # Create by object
    #
    def testCase000(self):
        """Check error condition.
        """
        _s = sys.path[:]
        A = os.path.normpath('a/A.txt')        #@UnusedVariable
        B = os.path.normpath('a/b/B.txt')      #@UnusedVariable
        C = os.path.normpath('a/b/c/C.txt')    #@UnusedVariable
        D = os.path.normpath('a/b/c/d/D.txt')  #@UnusedVariable

        start = None
        top = ''
        res = []
        try:
            ret = setUpperTreeSearchPath(start,top,res) #@UnusedVariable
        except FileSysObjectsException:
            pass
        else:
            raise
        pass

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        

    def testCase001(self):
        """Check error condition.
        """
        _s = sys.path[:]
        A = os.path.normpath('a/A.txt')        #@UnusedVariable
        B = os.path.normpath('a/b/B.txt')      #@UnusedVariable
        C = os.path.normpath('a/b/c/C.txt')    #@UnusedVariable
        D = os.path.normpath('a/b/c/d/D.txt')  #@UnusedVariable

        start = ''
        top = None
        res = []
        try:
            ret = setUpperTreeSearchPath(start,top,res) #@UnusedVariable
        except FileSysObjectsException:
            pass
        else:
            raise
        pass

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        

if __name__ == '__main__':
    unittest.main()
