from __future__ import absolute_import

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import tests.CheckEscUnesc

import filesysobjects.FileSysObjects

#
#######################
#


class CallUnits(tests.CheckEscUnesc.CheckEscUnesc):

    def testCase110(self):
        _in        = 'cifs://hostname/share\a/b/c'
        _esc     = r'cifs://hostname\\share\\a\\b\\c'
        _unesc = r'cifs://hostname\share\a\b\c'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase111(self):
        _in        = 'cifs://hostname////////////share\\\a\\\b///////////c'
        _esc     = r'cifs://hostname\\share\\a\\b\\c'
        _unesc = r'cifs://hostname\share\a\b\c'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

#
#######################
#

if __name__ == '__main__':
    unittest.main()
