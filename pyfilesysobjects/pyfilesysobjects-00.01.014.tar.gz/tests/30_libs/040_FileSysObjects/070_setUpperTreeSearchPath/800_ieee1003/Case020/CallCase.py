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
else:
    print >>sys.stderr, "ERROR:Requires Python-2.6(.6+) or 2.7"
    sys.exit(1)

import platform

from pysourceinfo.PySourceInfo import getPythonPathRel,getPythonPathFromSysPath
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,FileSysObjectsException,splitAppPrefix,getAppPrefixLocalPath,getTopFromPathString,unescapeFilePath
#from unittest.case import SkipTest


#
#######################
#
class CallUnits(unittest.TestCase):
    
    def testCase000(self):
        _s = sys.path[:]
        start = os.path.abspath(os.path.dirname(__file__))+os.path.normpath('/a/b/c')
        top = os.path.abspath(os.path.dirname(__file__))
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        myplist = [getTopFromPathString('tests',[os.path.dirname(__file__)+os.sep+start])]
        res = []
        for i in range(len(_res)):
            _p = getPythonPathRel(_res[i],myplist)
            if _p:
                res.append(_p) 
        resx = [
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020',
        ]        
        resx = map(os.path.normpath,resx)

        res = map(unescapeFilePath, res)
        resx = map(unescapeFilePath, resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == res
        pass

    def testCase001(self):

        _s = sys.path[:]
        
        start0 = os.path.abspath(os.path.dirname(__file__)+os.sep+os.path.normpath('/a/b/c'))
        d,p = os.path.splitdrive(start0)
        start1 = os.sep + p
    
        # normalize
        _start_elems = splitAppPrefix(start0,**{'ias':True})
        start= getAppPrefixLocalPath(_start_elems)

        assert start0 == start
        
        top = 'tests/'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'ias':True}) #@UnusedVariable

        myplist = [getTopFromPathString('tests',[start])]
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],myplist)) 
        resx = [
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath',
            '30_libs/040_FileSysObjects',
            '30_libs',
            '.',
        ]        
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == res
        pass

    def testCase002(self):

        _s = sys.path[:]
        
        start0 = os.path.abspath(os.path.dirname(__file__)+os.sep+os.path.normpath('/a/b/c'))
        d,p = os.path.splitdrive(start0)
        start1 = os.sep + p
    
        # normalize
        _start_elems = splitAppPrefix(start0,**{'ias':True})
        start= getAppPrefixLocalPath(_start_elems)

        assert start0 == start
        
        top = 'tests/'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'ias':True}) #@UnusedVariable

        myplist = [getTopFromPathString('tests',[start])]
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],myplist)) 
        resx = [
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath',
            '30_libs/040_FileSysObjects',
            '30_libs',
            '.',
        ]        
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == res
        pass

    def testCase010(self):

        #for now windows only
        #for now windows only
        if platform.system() != 'Windows':
            unittest.SkipTest("Requires Windows - skipped!")
            return True
        
        _s = sys.path[:]

        start0 = os.path.abspath(os.path.dirname(__file__)+os.sep+os.path.normpath('/a/b/c'))
        start1 = os.sep + start0
    
        # normalize
        _start_elems = splitAppPrefix(start0,**{'ias':True})
        start= getAppPrefixLocalPath(_start_elems)

        assert start0 == start

        top = 'file://'+os.path.splitdrive(os.path.abspath(os.path.dirname(__file__)))[1]

        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'ias':True}) #@UnusedVariable
        
        forDebugOnly = sys.path #@UnusedVariable
        
        myplist = [getTopFromPathString('tests',[start])]
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],myplist)) 

        resx = [
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a',
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020',
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == res
        pass

    def testCase012(self):

        if platform.system() != 'Windows':
            unittest.SkipTest("Requires Windows - skipped!")
            return True
       
        _s = sys.path[:]

        _share,start = os.path.splitdrive(os.path.abspath(os.path.dirname(__file__))+os.path.normpath('/a/b/c'))
        _share,top = os.path.splitdrive(os.path.abspath(os.path.dirname(__file__))+os.path.normpath('/a'))
        top = 'file://'+top
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res,**{'ias':True}) #@UnusedVariable
        
        forDebugOnly = sys.path #@UnusedVariable
        
        myplist = [getTopFromPathString('tests',[start])]
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],myplist)) 

        resx = [
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a'
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        

        assert resx == res
        pass

    def testCase013(self):

        if platform.system() != 'Windows':
            unittest.SkipTest("Requires Windows - skipped!")
            return True
        if not os.path.exists('\\\\localhost\\C$'):
            unittest.SkipTest("Requires share for this test - skipped!")
            return True
        
        _s = sys.path[:]

        _rtype = 'SHARE'
        _host = 'localhost'
        _share,sp = os.path.splitdrive(os.path.abspath(os.path.dirname(__file__))+os.path.normpath('/a/b/c'))
        _share = 'C$'
        start = getAppPrefixLocalPath((_rtype, _host, _share,sp,))

        _share,top = os.path.splitdrive(os.path.abspath(os.path.dirname(__file__))+os.path.normpath('/a'))
        top = 'file://'+top[1:]
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
        
        forDebugOnly = sys.path #@UnusedVariable
        
        myplist_elems = splitAppPrefix(start)
        myplist = [getTopFromPathString('tests',[start])]
        res = []
        for i in range(len(_res)):
            res.append(getPythonPathRel(_res[i],myplist)) 

        resx = [
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
            '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a'
        ]
        resx = map(os.path.normpath,resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        

        assert resx == res
        pass

#TODO:
#     def testCase015(self):
# 
#         #for now windows only
#         if platform.system() != 'Windows':
#             unittest.SkipTest("Requires Windows - skipped!")
#             return True
#         
#         _s = sys.path[:]
# 
#         start0 = os.path.abspath(os.path.dirname(__file__)+os.sep+os.path.normpath('/a/b/c'))
#         start1 = os.sep + start0
#     
#         # normalize
#         _start_elems = splitAppPrefix(start0,**{'ias':True})
#         start= getAppPrefixLocalPath(_start_elems)
# 
#         assert start0 == start
# 
#         top = 'file://'+os.sep+os.path.splitdrive(os.path.abspath(os.path.dirname(__file__)))[1]
# 
#         _res = []
#         ret = setUpperTreeSearchPath(start,top,_res,**{'ias':True}) #@UnusedVariable
#         
#         forDebugOnly = sys.path #@UnusedVariable
#         
#         myplist = [getTopFromPathString('tests',[start])]
#         res = []
#         for i in range(len(_res)):
#             res.append(getPythonPathRel(_res[i],myplist)) 
# 
#         resx = [
#             '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b/c', 
#             '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a/b', 
#             '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/800_ieee1003/Case020/a'
#         ]
#         resx = map(os.path.normpath,resx)
# 
#         [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
#         sys.path.extend(_s)
        

        assert resx == res
        pass


if __name__ == '__main__':
    unittest.main()
