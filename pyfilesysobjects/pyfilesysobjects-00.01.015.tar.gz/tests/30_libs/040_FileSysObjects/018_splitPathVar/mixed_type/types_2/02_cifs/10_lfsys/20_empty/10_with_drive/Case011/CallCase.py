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

    def testCase003(self):
        apstr = 'cifs://'+filesysobjects.FileSysObjects.normpathX('hostname/share/a/b/c')
        apstr += os.pathsep + filesysobjects.FileSysObjects.normpathX('d:hostname/share/a/b/c')
        apstr += os.pathsep + 'cifs://'+filesysobjects.FileSysObjects.normpathX('hostname/share/a/b/c')
        apstr += os.pathsep + filesysobjects.FileSysObjects.normpathX('d:hostname/share/a/b/c')
        apstr += os.pathsep + 'cifs://'+filesysobjects.FileSysObjects.normpathX('hostname/share/a/b/c')
        apstr += os.pathsep + filesysobjects.FileSysObjects.normpathX('d:hostname/share/a/b/c')
        retRef = [
            ('CIFS','hostname', 'share', filesysobjects.FileSysObjects.normpathX('a/b/c')),
            ('LDSYS','', 'd:', filesysobjects.FileSysObjects.normpathX('hostname/share/a/b/c')),
            ('CIFS','hostname', 'share', filesysobjects.FileSysObjects.normpathX('a/b/c')),
            ('LDSYS','', 'd:', filesysobjects.FileSysObjects.normpathX('hostname/share/a/b/c')),
            ('CIFS','hostname', 'share', filesysobjects.FileSysObjects.normpathX('a/b/c')),
            ('LDSYS','', 'd:', filesysobjects.FileSysObjects.normpathX('hostname/share/a/b/c')),
        ]
        ret = filesysobjects.FileSysObjects.splitPathVar(apstr,appsplit=True)
        self.assertEqual(retRef, ret)

#
#######################
#

if __name__ == '__main__':
    unittest.main()

