"""Check IEEE1003.1-Chap. 4.2.
"""
from __future__ import absolute_import

import os,sys
version = '{0}.{1}'.format(*sys.version_info[:2])
if version in ('2.6',): # pragma: no cover
    import unittest2 as unittest
    from unittest2 import SkipTest
elif version in ('2.7',): # pragma: no cover
    import unittest
    from unittest import SkipTest
    #from unittest.case import SkipTest
else:
    print >>sys.stderr, "ERROR:Requires Python-2.6(.6+) or 2.7"
    sys.exit(1)

import platform

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,normpathX,getTopFromPathString


#
#######################
#
class UseCase(unittest.TestCase):
    
    def testCase_drive_and_share_path(self):
        _s = sys.path[:]
        start = os.path.abspath(os.path.dirname(__file__)+os.path.normpath('/a/b/c'))
        top = os.path.dirname(start)
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        myplist = [getTopFromPathString('AppPathSyntax',[os.path.dirname(__file__)+os.sep+start])]
        res = []
        for i in range(len(_res)):
            _p = getPythonPathRel(_res[i],myplist)
            if _p:
                res.append(_p) 
        resx =   ['win_drive\\drive_and_share_path\\a\\b\\c', 'win_drive\\drive_and_share_path\\a\\b']
        res = map(normpathX, res)
        resx = map(normpathX, resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        self.assertEqual(resx, res)
        pass


if __name__ == '__main__':
    unittest.main()
