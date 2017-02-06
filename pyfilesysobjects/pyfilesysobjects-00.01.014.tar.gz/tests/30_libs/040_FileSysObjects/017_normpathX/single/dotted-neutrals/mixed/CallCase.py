from __future__ import absolute_import
from linecache import getline

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os,platform
import tests.CheckEscUnesc

from filesysobjects.FileSysObjects import normpathX
#
#######################
#


class CallUnits(tests.CheckEscUnesc.CheckEscUnesc):

    def testCase110(self):
        _in        = r'file:///./file_at_current_dir'
        if platform.system() == 'Windows':
            _esc     = r'file://\\file_at_current_dir'
            _unesc = r'file://\file_at_current_dir'
        else:
            _esc     = r'file:///file_at_current_dir'
            _unesc = r'file:///file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase120(self):
        _in        = r'file:////////////.//////file_at_current_dir'
        _esc     = r'file://\\file_at_current_dir'
        _unesc = r'file://\file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc,'b')

    def testCase200(self):
        _in        = r'file:////./file_at_current_dir'
        if platform.system() == 'Windows':
            _esc     = r'file://\\file_at_current_dir'
            _unesc = r'file://\file_at_current_dir'
        else:
            _esc     = r'file:///file_at_current_dir'
            _unesc = r'file:///file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc)

#
#######################
#

if __name__ == '__main__':
    unittest.main()

