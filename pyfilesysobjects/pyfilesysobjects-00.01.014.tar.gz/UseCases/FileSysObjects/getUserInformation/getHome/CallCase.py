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

from filesysobjects.FileSysObjects import getHome

#
#######################
#

class UseCase(unittest.TestCase):

    def testCase000(self):
        """just do it...
        """
        if sys.platform in ('win32',):
            self.assertEqual(getHome(), os.environ['HOMEDRIVE']+os.environ['HOMEPATH'])
        elif sys.platform in ('linux2', 'cygwin', 'darwin', ):
            self.assertEqual(getHome(), os.environ['HOME'])
        else: # eventually may not yet work if not unix
            self.assertEqual(getHome(), os.environ['HOME'])
        pass
 
#
#######################
#

if __name__ == '__main__':
    unittest.main()

