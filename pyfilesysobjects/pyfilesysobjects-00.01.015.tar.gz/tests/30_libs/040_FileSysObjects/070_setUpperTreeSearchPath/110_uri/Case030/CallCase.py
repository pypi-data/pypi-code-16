"""Check IEEE1003.1-Chap. 4.2.
"""
from __future__ import absolute_import

import unittest
import os,sys

from pysourceinfo.PySourceInfo import getPythonPathRel
from filesysobjects.FileSysObjects import setUpperTreeSearchPath,normpathX


#
#######################
#
class CallUnits(unittest.TestCase):

    def testCase000(self):
        _s = sys.path[:]
        A = os.path.normpath('a/A.txt')         #@UnusedVariable
        B = os.path.normpath('a/b/B.txt')       #@UnusedVariable
        C = os.path.normpath('a/b/c/C.txt')     #@UnusedVariable
        D = os.path.normpath('a/b/c/d/D.txt')   #@UnusedVariable

        start = 'file://'+os.path.abspath(os.path.dirname(__file__)+os.sep+D)
        top = 'file://a/b'
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
        
        mypos = os.path.abspath(os.path.normpath(os.path.dirname(__file__)+"/../../"))   
        res = []
        for i in range(len(_res)):
            pr = getPythonPathRel(_res[i],[mypos])
            if pr:
                res.append(pr)
        resx = ['110_uri/Case030/a/b/c/d', '110_uri/Case030/a/b/c', '110_uri/Case030/a/b']
        res = map(normpathX, res)
        resx = map(normpathX, resx)
        
        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        

        assert resx == res
        pass

    def testCase001(self):
        _s = sys.path[:]
        A = os.path.normpath('a/A.txt')         #@UnusedVariable
        B = os.path.normpath('a/b/B.txt')       #@UnusedVariable
        C = os.path.normpath('a/b/c/C.txt')     #@UnusedVariable
        D = os.path.normpath('a/b/c/d/D.txt')   #@UnusedVariable

        start = 'file://'+os.path.normpath(os.path.abspath(os.path.dirname(__file__)+os.sep+D))
        top = 'file://'+os.path.normpath('a/b')
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        mypos = os.path.abspath(os.path.normpath(os.path.dirname(__file__)+"/../../"))   
        res = []
        for i in range(len(_res)):
            pr = getPythonPathRel(_res[i],[mypos])
            if pr:
                res.append(pr)
        resx =  ['110_uri\\Case030\\a\\b\\c\\d', '110_uri\\Case030\\a\\b\\c', '110_uri\\Case030\\a\\b']
        res = map(normpathX, res)
        resx = map(normpathX, resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        self.assertEqual(resx, res)
        pass

    def testCase002(self):
        _s = sys.path[:]
        A = os.path.normpath('a/A.txt')         #@UnusedVariable
        B = os.path.normpath('a/b/B.txt')       #@UnusedVariable
        C = os.path.normpath('a/b/c/C.txt')     #@UnusedVariable
        D = os.path.normpath('a/b/c/d/D.txt')   #@UnusedVariable

        start = 'file://'+os.path.normpath(os.path.abspath(os.path.dirname(__file__)+os.sep+D))
        top = 'file://'+os.path.normpath('a/b')
        _res = []
        ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable

        mypos = os.path.abspath(os.path.normpath(os.path.dirname(__file__)+"/../../"))   
        res = []
        for i in range(len(_res)):
            pr = getPythonPathRel(_res[i],[mypos])
            if pr:
                res.append(pr)
        resx =  ['110_uri\\Case030\\a\\b\\c\\d', '110_uri\\Case030\\a\\b\\c', '110_uri\\Case030\\a\\b']
        res = map(normpathX, res)
        resx = map(normpathX, resx)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        assert resx == res
        pass

#FIXME: seems to be not required for now
#     def testCase010(self):
#         _s = sys.path[:]
#         A = os.path.normpath('a/A.txt')         #@UnusedVariable
#         B = os.path.normpath('a/b/B.txt')       #@UnusedVariable
#         C = os.path.normpath('a/b/c/C.txt')     #@UnusedVariable
#         D = os.path.normpath('a/b/c/d/D.txt')   #@UnusedVariable
# 
#         start = 'file://'+os.path.normpath(os.path.abspath(os.path.dirname(__file__)+os.sep+D))
# #        top = 'file://'+os.path.normpath('a/b')
#         top = os.path.normpath('a/b')
#         _res = []
#         ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
# 
#         forDebugOnly = sys.path #@UnusedVariable
#         
#         res = []
#         for i in range(len(_res)):
#             res.append(getPythonPathRel(_res[i])) 
#         resx = [
#             '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b/c/d', 
#             '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b/c', 
#             '30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b'
# #             'tests/30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b/c/d', 
# #             'tests/30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b/c', 
# #             'tests/30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b'
#         ]
#         resx = map(os.path.normpath,resx)
# 
#         [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
#         sys.path.extend(_s)
#         
#         
#         print
#         print("-----")
#         print("4TEST:resx=  "+str(resx))
#         print("-----")
#         print("4TEST:res =   "+str(res))
# 
#         self.assertEqual(resx,res)
#         pass

    def testCase011(self):
#FIXME:
#         _s = sys.path[:]
#         A = os.path.normpath('a/A.txt')         #@UnusedVariable
#         B = os.path.normpath('a/b/B.txt')       #@UnusedVariable
#         C = os.path.normpath('a/b/c/C.txt')     #@UnusedVariable
#         D = os.path.normpath('a/b/c/d/D.txt')   #@UnusedVariable
# 
#         start = 'file://///'+os.path.normpath(os.path.abspath(os.path.dirname(__file__)+os.sep+D))
#         top = 'file://///'+os.path.normpath('a/b')
#         _res = []
#         ret = setUpperTreeSearchPath(start,top,_res) #@UnusedVariable
# 
#         forDebugOnly = sys.path #@UnusedVariable
#         
#         res = []
#         for i in range(len(_res)):
#             res.append(getPythonPathRel(_res[i])) 
#         resx = [
#             'tests/30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b/c/d', 
#             'tests/30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b/c', 
#             'tests/30_libs/040_FileSysObjects/070_setUpperTreeSearchPath/110_uri/Case030/a/b'
#         ]
#         resx = map(os.path.normpath, resx)
# 
#         [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
#         sys.path.extend(_s)
# 
#         assert resx == res
        pass


if __name__ == '__main__':
    unittest.main()
