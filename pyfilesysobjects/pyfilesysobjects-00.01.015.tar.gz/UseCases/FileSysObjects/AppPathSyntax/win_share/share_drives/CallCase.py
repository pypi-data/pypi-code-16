"""Demonstrates the application of hierarchical search paths on shared drives on Microsoft-Windows(TM).

Type: SHARE

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
else:
    print >>sys.stderr, "ERROR:Requires Python-2.6(.6+) or 2.7"
    sys.exit(1)

import platform

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,getAppPrefixLocalPath,getTopFromPathString


#
#######################
#
class UseCase(unittest.TestCase):

    def testCase_SharedDriveC(self):
        #for now windows only
        if platform.system() != 'Windows':
            unittest.SkipTest("Requires Windows - skipped!")
            return True
        if not os.path.exists('\\\\localhost\\C$'):
            unittest.SkipTest("Requires share for this test - skipped!")
            return True

        _s = sys.path[:]

        _rtype = 'SHARE'
        _host = 'localhost'
        _share,sp = os.path.splitdrive(os.path.abspath(os.path.dirname(__file__))+os.path.normpath('/a/b///c/d/b/c///'))
        _share = 'C$'
        start = getAppPrefixLocalPath((_rtype, _host, _share,sp,))

        s = os.sep

        _rtype = 'SHARE'
        _host = 'localhost'
        sp = s+os.sep.join(sp.split(os.sep)[1:5])+s
        #sp = 2*s+os.sep.join(sp.split(os.sep)[1:5])+s
        _share = 'C$'
        top = getAppPrefixLocalPath((_rtype, _host, _share,sp,))

        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'reverse':True,}) #@UnusedVariable

        forDebugOnly = sys.path #@UnusedVariable

        _rtype = 'SHARE'
        _host = 'localhost'
        _share = 'C$'
        sp = sp
        mystart = getAppPrefixLocalPath((_rtype, _host, _share,sp,))

        mystart  = getTopFromPathString(top,[mystart])
        myplist = [mystart,]
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],myplist))

        resx = [
            '.',
            'FileSysObjects',
            'FileSysObjects/AppPathSyntax',
            'FileSysObjects/AppPathSyntax/win_share',
            'FileSysObjects/AppPathSyntax/win_share/share_drives',
            'FileSysObjects/AppPathSyntax/win_share/share_drives/a',
            'FileSysObjects/AppPathSyntax/win_share/share_drives/a/b',
            'FileSysObjects/AppPathSyntax/win_share/share_drives/a/b/c',
            'FileSysObjects/AppPathSyntax/win_share/share_drives/a/b/c/d',
            'FileSysObjects/AppPathSyntax/win_share/share_drives/a/b/c/d/b',
            'FileSysObjects/AppPathSyntax/win_share/share_drives/a/b/c/d/b/c',
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)

        assert resx == res
        pass

if __name__ == '__main__':
    unittest.main()

