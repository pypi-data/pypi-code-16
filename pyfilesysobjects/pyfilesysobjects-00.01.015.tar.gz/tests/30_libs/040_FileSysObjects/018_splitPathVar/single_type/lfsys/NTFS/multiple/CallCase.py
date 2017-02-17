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

#
#######################
#


class CallUnits(unittest.TestCase):

    def testCase010(self):
        apstr = filesysobjects.FileSysObjects.normpathX('a/b/c'+os.pathsep+'/d/e',**{'tpf':'win'})
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**{'tpf':'win','appsplit':True,})
        retRef = [
            ('LFSYS','', '', filesysobjects.FileSysObjects.normpathX('a/b/c',**{'tpf':'win'})),
            ('LFSYS','', '', filesysobjects.FileSysObjects.normpathX('/d/e',**{'tpf':'win'})),
        ]
        self.assertEqual(retRef, ret)

    def testCase020(self):
        apstr = filesysobjects.FileSysObjects.normpathX('a/b/c'+os.pathsep+'/d/e'+os.pathsep+'/f/g')
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,**{'tpf':'win','appsplit':True,})
        retRef = [
            ('LFSYS','', '', filesysobjects.FileSysObjects.normpathX('a/b/c',**{'tpf':'win'})),
            ('LFSYS','', '', filesysobjects.FileSysObjects.normpathX('/d/e',**{'tpf':'win'})),
            ('LFSYS','', '', filesysobjects.FileSysObjects.normpathX('/f/g',**{'tpf':'win'})),
        ]
        self.assertEqual(retRef, ret)


#
#######################
#

if __name__ == '__main__':
    unittest.main()

