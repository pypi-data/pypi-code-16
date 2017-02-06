from __future__ import absolute_import
from linecache import getline


__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,sys

import filesysobjects.FileSysObjects
import pysourceinfo.PySourceInfo

#
#######################
#


class CallUnits(unittest.TestCase):

    def testCase000(self):

        start = os.path.dirname(__file__)+os.sep+'a/tests//////a/b/tests//c////////d/tests/b///c'
        #top = '/////tests///'
        top = 'tests///'
        top = filesysobjects.FileSysObjects.getTopFromPathString(top, [start]) #@UnusedVariable
        top0ref=os.path.abspath(os.path.dirname(__file__)+'/../../../../../')

        self.assertEqual(top0ref, os.path.abspath(top)) 
        pass


#
#######################
#

if __name__ == '__main__':
    unittest.main()

