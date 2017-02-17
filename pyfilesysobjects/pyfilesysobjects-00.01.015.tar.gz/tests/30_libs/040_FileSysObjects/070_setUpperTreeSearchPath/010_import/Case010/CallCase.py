from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='202b4a86-488d-4d9b-856e-4aa7fd05b1e5'

__docformat__ = "restructuredtext en"

import unittest
import os,sys


#
#######################
#

class CallUnits(unittest.TestCase):
    

    
    

    def testCase000(self):
        _s = sys.path[:]
        #
        # set search for the call of 'myscript.sh'
        from filesysobjects.FileSysObjects import setUpperTreeSearchPath
        start = os.path.abspath(os.path.dirname(__file__))        
        setUpperTreeSearchPath(start,'pyfilesysobjects')
        
        from tests.dummymodules.Dummy1 import Dummy1
        from tests.dummymodules.Dummy0 import Dummy0
        
        d = Dummy0()
        d.set(1)

        [ sys.path.pop() for x in range(len(sys.path)) ] #@UnusedVariable
        sys.path.extend(_s)
        
        pass

#
#######################
#

if __name__ == '__main__':
    unittest.main()

