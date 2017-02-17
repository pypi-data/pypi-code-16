from __future__ import absolute_import
from linecache import getline

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import os
import platform
import tests.CheckEscUnesc

from filesysobjects.FileSysObjects import normpathX
#
#######################
#


class UseCase(tests.CheckEscUnesc.CheckEscUnesc):

    def testCase010(self):
        _in        = r'\\host\share'
        _esc     = r'\\\\host\\share'
        _unesc = r'\\host\share'
        self.check_esc_unesc(_in,_esc,_unesc,'b')
        
    def testCase010a(self):
        _in        = r'smb://host/share'
        if platform.system() == 'Windows':
            _esc     = r'smb://host\\share'
            _unesc = r'smb://host\share'
        else:
            _esc     = r'smb://host/share'
            _unesc = r'smb://host/share'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase020(self):
        _in        = '\\\\host\share\dirpath'
        if platform.system() == 'Windows':
            _esc     = r'\\\\host\\share\\dirpath'
            _unesc = r'\\host\share\dirpath'
        else:
            _esc     = r'//host/share/dirpath'
            _unesc = r'//host/share/dirpath'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase020a(self):
        _in        = 'smb://host/share/dirpath'
        if platform.system() == 'Windows':
            _esc     = r'smb://host\\share\\dirpath'
            _unesc = r'smb://host\share\dirpath'
        else:
            _esc     = r'smb://host/share/dirpath'
            _unesc = r'smb://host/share/dirpath'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase030(self):
        _in        = '\\\\host\share\dirpath\filename'
        if platform.system() == 'Windows':
            _esc     = r'\\\\host\\share\\dirpath\\filename'
            _unesc = r'\\host\share\dirpath\filename'
        else:
            _esc     = r'//host/share/dirpath/filename'
            _unesc = r'//host/share/dirpath/filename'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase030a(self):
        _in        = r'smb://host/share/dirpath/filename'
        if platform.system() == 'Windows':
            _esc     = r'smb://host\\share\\dirpath\\filename'
            _unesc = r'smb://host\share\dirpath\filename'
        else:
            _esc     = r'smb://host/share/dirpath/filename'
            _unesc = r'smb://host/share/dirpath/filename'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase040(self):
        _in        = r'smb://host/share/'
        if platform.system() == 'Windows':
            _esc     = r'smb://host\\share'
            _unesc = r'smb://host\share'
        else:
            _esc     = r'smb://host/share'
            _unesc = r'smb://host/share'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase050(self):
        _in        = r'smb://host/share/dirpath'
        if platform.system() == 'Windows':
            _esc     = r'smb://host\\share\\dirpath'
            _unesc = r'smb://host\share\dirpath'
        else:
            _esc     = r'smb://host/share/dirpath'
            _unesc = r'smb://host/share/dirpath'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase060(self):
        _in        = r'smb://host/share/name'
        if platform.system() == 'Windows':
            _esc     = r'smb://host\\share\\name'
            _unesc = r'smb://host\share\name'
        else:
            _esc     = r'smb://host/share/name'
            _unesc = r'smb://host/share/name'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase070(self):
        _in        = r'smb://host/share/dirpath/name'
        if platform.system() == 'Windows':
            _esc     = r'smb://host\\share\\dirpath\\name'
            _unesc = r'smb://host\share\dirpath\name'
        else:
            _esc     = r'smb://host/share/dirpath/name'
            _unesc = r'smb://host/share/dirpath/name'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase080(self):
        _in        = r'smb://WORKGROUP@host/share'
        if platform.system() == 'Windows':
            _esc     = r'smb://WORKGROUP@host\\share'
            _unesc = r'smb://WORKGROUP@host\share'
        else:
            _esc     = r'smb://WORKGROUP@host/share'
            _unesc = r'smb://WORKGROUP@host/share'
        self.check_esc_unesc(_in,_esc,_unesc)

    def testCase090(self):
        _in        = r'smb://WORKGROUP;User@host/share'
        if platform.system() == 'Windows':
            _esc     = r'smb://WORKGROUP;User@host\\share'
            _unesc = r'smb://WORKGROUP;User@host\share'
        else:
            _esc     = r'smb://WORKGROUP;User@host/share'
            _unesc = r'smb://WORKGROUP;User@host/share'
        self.check_esc_unesc(_in,_esc,_unesc)
#
#######################
#

if __name__ == '__main__':
    unittest.main()
