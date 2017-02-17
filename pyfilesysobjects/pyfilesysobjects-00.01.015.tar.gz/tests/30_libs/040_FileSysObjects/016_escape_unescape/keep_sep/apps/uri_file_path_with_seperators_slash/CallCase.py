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

    def testCase120(self):
        _in        = 'file://///hostname/share/a/b/c'
        _esc     = 'file://///hostname/share/a/b/c'
        _unesc = 'file://///hostname/share/a/b/c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase121(self):
        _in        = 'file://///hostname/share//////////////a///b/c'
        _esc     = 'file://///hostname/share/a/b/c'
        _unesc = 'file://///hostname/share/a/b/c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase130(self):
        _in        = 'file://hostname/share/a/b/c'
        _esc     = 'file://hostname/share/a/b/c'
        _unesc = 'file://hostname/share/a/b/c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase131(self):
        _in        = 'file://hostname/share//////////////a///b/c'
        _esc     = 'file://hostname/share/a/b/c'
        _unesc = 'file://hostname/share/a/b/c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase140(self):
        _in        = 'file:///hostname/share/a/b/c'
        _esc     = 'file:///hostname/share/a/b/c'
        _unesc = 'file:///hostname/share/a/b/c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase141(self):
        _in        = 'file:///hostname/share//////////////a///b/c'
        _esc     = 'file:///hostname/share/a/b/c'
        _unesc = 'file:///hostname/share/a/b/c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase150(self):
        _in        = 'file:////////hostname/share/a/b/c'
        _esc     = 'file:///hostname/share/a/b/c'
        _unesc = 'file:///hostname/share/a/b/c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase151(self):
        _in        = 'file:////////hostname/share//////////////a///b/c'
        _esc     = 'file:///hostname/share/a/b/c'
        _unesc = 'file:///hostname/share/a/b/c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')



#
#######################
#

if __name__ == '__main__':
    unittest.main()
