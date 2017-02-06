from __future__ import absolute_import

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.1'
__uuid__='af90cc0c-de54-4a32-becd-06f5ce5a3a75'

__docformat__ = "restructuredtext en"

import unittest
import tests.CheckEscUnesc

#
#######################
#


class CallUnits(tests.CheckEscUnesc.CheckEscUnesc):
    
    def testCase_a0(self):
        _in        = '/a'
        _esc     = r'\\a'
        _unesc = r'\a' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_b(self):
        _in        = '/b'
        _esc     = r'\\b'
        _unesc = r'\b' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_c(self):
        _in        = '/c'
        _esc     = r'\\c'
        _unesc = r'\c' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_d(self):
        _in        = '/d'
        _esc     = r'\\d'
        _unesc = r'\d' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_e(self):
        _in        = '/e'
        _esc     = r'\\e'
        _unesc = r'\e' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_f(self):
        _in        = '/f'
        _esc     = r'\\f'
        _unesc = r'\f' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_g(self):
        _in        = '/g'
        _esc     = r'\\g'
        _unesc = r'\g' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_h(self):
        _in        = '/h'
        _esc     = r'\\h'
        _unesc = r'\h' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_i(self):
        _in        = '/i'
        _esc     = r'\\i'
        _unesc = r'\i' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_j(self):
        _in        = '/j'
        _esc     = r'\\j'
        _unesc = r'\j' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_k(self):
        _in        = '/k'
        _esc     = r'\\k'
        _unesc = r'\k' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_l(self):
        _in        = '/l'
        _esc     = r'\\l'
        _unesc = r'\l' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_m(self):
        _in        = '/m'
        _esc     = r'\\m'
        _unesc = r'\m' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_n(self):
        _in        = '/n'
        _esc     = r'\\n'
        _unesc = r'\n' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_o(self):
        _in        = '/r'
        _esc     = r'\\r'
        _unesc = r'\r' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_p(self):
        _in        = '/p'
        _esc     = r'\\p'
        _unesc = r'\p' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_q(self):
        _in        = '/q'
        _esc     = r'\\q'
        _unesc = r'\q' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_r(self):
        _in        = '/r'
        _esc     = r'\\r'
        _unesc = r'\r' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_s(self):
        _in        = '/s'
        _esc     = r'\\s'
        _unesc = r'\s' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_t(self):
        _in        = '/t'
        _esc     = r'\\t'
        _unesc = r'\t' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_u(self):
        _in        = '/u'
        _esc     = r'\\u'
        _unesc = r'\u' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_v(self):
        _in        = '/v'
        _esc     = r'\\v'
        _unesc = r'\v' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_w(self):
        _in        = '/w'
        _esc     = r'\\w'
        _unesc = r'\w' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_x(self):
        _in        = '/' + 'x'
        _esc     = r'\\x'
        _unesc = r'\x' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_y(self):
        _in        = '/y'
        _esc     = r'\\y'
        _unesc = r'\y' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

    def testCase_z(self):
        _in        = '/z'
        _esc     = r'\\z'
        _unesc = r'\z' 
        self.check_esc_unesc(_in,_esc,_unesc, 'b')

#
#######################
#

if __name__ == '__main__':
    unittest.main()

