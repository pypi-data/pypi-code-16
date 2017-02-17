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

    def testCase111(self):
        _in        = r'file:///./file_at_current_dir'
        _esc     = r'file://\\file_at_current_dir'
        _unesc = r'file://\file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase112(self):
        _in        = r'file:///./file_at_current_dir'
        _esc     = r'file://\\file_at_current_dir'
        _unesc = r'file://\file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase120(self):
        _in        = r'file:////////////.//////file_at_current_dir'
        _esc     = r'file://\\file_at_current_dir'
        _unesc = r'file://\file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase121(self):
        _in        = r'file://////.//////////file_at_current_dir'
        _esc     = r'file://\\file_at_current_dir'
        _unesc = r'file://\file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase122(self):
        _in        = r'file://////////////////////////.//file_at_current_dir'
        _esc     = r'file://\\file_at_current_dir'
        _unesc = r'file://\file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase123(self):
        _in        = r'file:///./////file_at_current_dir///////////////////////'
        _esc     = r'file://\\file_at_current_dir'
        _unesc = r'file://\file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

#FIXME: really rare but an error
#     def testCase160(self):
#         _in        = r'file://///.//////////file_at_current_dir'
#         _esc     = r'file://\\file_at_current_dir'
#         _unesc = r'file://\file_at_current_dir'
#         self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase300(self):
        _in        = r'./file_at_current_dir'
        _esc     = r'file_at_current_dir'
        _unesc = r'file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase301(self):
        _in        = r'./////////////////file_at_current_dir'
        _esc     = r'file_at_current_dir'
        _unesc = r'file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase400(self):
        _in        = r'file://./file_at_current_dir'
        _esc     = r'file://file_at_current_dir'
        _unesc = r'file://file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')
  
    def testCase401(self):
        _in        = r'file://././././././././././file_at_current_dir'
        _esc     = r'file://file_at_current_dir'
        _unesc = r'file://file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase402(self):
        _in        = r'file://././././file_at_current_dir/././././.'
        _esc     = r'file://file_at_current_dir'
        _unesc = r'file://file_at_current_dir'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase403(self):
        _in        = r'file://x/file_at_current_dir/..'
        _esc     = r'file://x'
        _unesc = 'file://x'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')
  
    def testCase404(self):
        _in        = r'file://file_at_current_dir/..'
        _esc     = r'file://'
        _unesc = 'file://'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase408(self):
        _in        = r'file:///file_at_current_dir/..'
        _esc     = r'file://\\'
        _unesc = 'file://\\'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')
  
    def testCase409(self):
        _in        = r'file:///file_at_current_dir/../a/b/c/..'
        _esc     = r'file://\\a\\b'
        _unesc = r'file://\a\b'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')
  
    def testCase410(self):
        _in        = r'file:///file_at_current_dir/../a/b/c/../d/../e/../f/./g///////./././////.'
        _esc     = r'file://\\a\\b\\f\\g'
        _unesc = r'file://\a\b\f\g'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase411(self):
        _in        = r'file://./././file_at_current_dir/././/a//././b/././'
        _esc     = r'file://file_at_current_dir\\a\\b'
        _unesc = r'file://file_at_current_dir\a\b'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase500(self):
        _in        = r'file://./file_at_current_dir/a/b/'
        _esc     = r'file://file_at_current_dir\\a\\b'
        _unesc = r'file://file_at_current_dir\a\b'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase501(self):
        _in        = r'file://./file_at_current_dir/a/../b'
        _esc     = r'file://file_at_current_dir\\b'
        _unesc = r'file://file_at_current_dir\b'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase510(self):
        _in        = r'file://./file_at_current_dir/a/b/..'
        _esc     = r'file://file_at_current_dir\\a'
        _unesc = r'file://file_at_current_dir\a'
        self.check_esc_unesc(_in,_esc,_unesc, 'b')


#
#######################
#

if __name__ == '__main__':
    unittest.main()

