"""Get the caller name.
"""
from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,sys

import filesysobjects.FileSysObjects
import pysourceinfo

#
#######################
#


class UseCase(unittest.TestCase):

    def root_from_string(self):
        _s = sys.path[:]
        #
        # prefix from unchanged sys.path
        mySysPathPrefixRaw = pysourceinfo.PySourceInfo.getPythonPathFromSysPath(__file__)
        
        myTestPath0 = os.sep+'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'+os.sep+'e'+os.sep+'f'+os.sep+'g'+os.sep+'h'
        myTestPath1 = myTestPath0 + myTestPath0
        myTestPath2 = myTestPath1 + myTestPath0 #@UnusedVariable
        
        #
        # set search for the call of 'myscript.sh'
        from filesysobjects.FileSysObjects import setUpperTreeSearchPath
        setUpperTreeSearchPath(None,'UseCases'+os.sep)


        px = filesysobjects.FileSysObjects.getTopFromPathString(
            'd'+os.sep,[myTestPath1]
        )

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        

        pxn = os.sep+'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'
        assert pxn == px
        pass

    def root_from_string_matchlvl0(self):
        _s = sys.path[:]
        #
        # prefix from unchanged sys.path
        mySysPathPrefixRaw = pysourceinfo.PySourceInfo.getPythonPathFromSysPath(__file__)
        
        myTestPath0 = os.sep+'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'+os.sep+'e'+os.sep+'f'+os.sep+'g'+os.sep+'h'
        myTestPath1 = myTestPath0 + myTestPath0
        myTestPath2 = myTestPath1 + myTestPath0
        
        #
        # set search for the call of 'myscript.sh'
        from filesysobjects.FileSysObjects import setUpperTreeSearchPath
        setUpperTreeSearchPath(None,'UseCases'+os.sep)

        px = filesysobjects.FileSysObjects.getTopFromPathString(
            'd'+os.sep,[myTestPath1],**{'matchlvl':0}
        )

        pxn = os.sep+'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        
        assert pxn == px
        pass

    def root_from_string_matchlvl1(self):
        _s = sys.path[:]
        #
        # prefix from unchanged sys.path
        mySysPathPrefixRaw = pysourceinfo.PySourceInfo.getPythonPathFromSysPath(__file__)
        
        myTestPath0 = os.sep+'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'+os.sep+'e'+os.sep+'f'+os.sep+'g'+os.sep+'h'
        myTestPath1 = myTestPath0 + myTestPath0
        myTestPath2 = myTestPath1 + myTestPath0 #@UnusedVariable
        
        #
        # set search for the call of 'myscript.sh'
        from filesysobjects.FileSysObjects import setUpperTreeSearchPath
        setUpperTreeSearchPath(None,os.sep+'UseCases'+os.sep)

        px = filesysobjects.FileSysObjects.getTopFromPathString(
            'd'+os.sep,[myTestPath1],**{'matchlvl':1}
        )

        pxn = myTestPath0 +os.sep+ 'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        
        assert pxn == px
        pass

    def testCase003(self):
        _s = sys.path[:]
        #
        # prefix from unchanged sys.path
        mySysPathPrefixRaw = pysourceinfo.PySourceInfo.getPythonPathFromSysPath(__file__)
        
        myTestPath0 = os.sep+'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'+os.sep+'e'+os.sep+'f'+os.sep+'g'+os.sep+'h'
        myTestPath1 = myTestPath0 + myTestPath0
        myTestPath2 = myTestPath1 + myTestPath0
        
        #
        # set search for the call of 'myscript.sh'
        from filesysobjects.FileSysObjects import setUpperTreeSearchPath
        setUpperTreeSearchPath(os.path.abspath(os.path.dirname(__file__)),'UseCases'+os.sep)

        px = filesysobjects.FileSysObjects.getTopFromPathString(
            'd'+os.sep,[myTestPath2],**{'matchlvl':2}
        )

        pxn = myTestPath1 +os.sep+ 'a'+os.sep+'b'+os.sep+'c'+os.sep+'d'

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        
        assert pxn == px
        pass

if __name__ == '__main__':
    unittest.main()

