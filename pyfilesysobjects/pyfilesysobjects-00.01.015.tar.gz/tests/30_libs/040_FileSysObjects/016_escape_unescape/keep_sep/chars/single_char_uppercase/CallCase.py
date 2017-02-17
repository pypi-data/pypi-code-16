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
        _in        = '\A'
        _esc     = r'\\A'
        _unesc = r'\A' 
        self.check_esc_unesc(_in,_esc,_unesc,'k')

    def testCase_b(self):
        _in        = '\B'
        _esc     = r'\\B'
        _unesc = r'\B' 
        self.check_esc_unesc(_in,_esc,_unesc,'k')

    def testCase_c(self):
        _in        = '\C'
        _esc     = r'\\C'
        _unesc = r'\C' 
        self.check_esc_unesc(_in,_esc,_unesc,'k')

    def testCase_d(self):
        _in        = '\D'
        _esc     = r'\\D'
        _unesc = r'\D' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_e(self):
        _in        = '\E'
        _esc     = r'\\E'
        _unesc = r'\E' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_f(self):
        _in        = '\F'
        _esc     = r'\\F'
        _unesc = r'\F' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_g(self):
        _in        = '\G'
        _esc     = r'\\G'
        _unesc = r'\G' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_h(self):
        _in        = '\H'
        _esc     = r'\\H'
        _unesc = r'\H' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_i(self):
        _in        = '\I'
        _esc     = r'\\I'
        _unesc = r'\I' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_j(self):
        _in        = '\J'
        _esc     = r'\\J'
        _unesc = r'\J' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_k(self):
        _in        = '\K'
        _esc     = r'\\K'
        _unesc = r'\K' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_l(self):
        _in        = '\L'
        _esc     = r'\\L'
        _unesc = r'\L' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_m(self):
        _in        = '\M'
        _esc     = r'\\M'
        _unesc = r'\M' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_n(self):
        _in        = '\N'
        _esc     = r'\\N'
        _unesc = r'\N' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_o(self):
        _in        = '\R'
        _esc     = r'\\R'
        _unesc = r'\R' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_p(self):
        _in        = '\P'
        _esc     = r'\\P'
        _unesc = r'\P' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_q(self):
        _in        = '\Q'
        _esc     = r'\\Q'
        _unesc = r'\Q' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_r(self):
        _in        = '\R'
        _esc     = r'\\R'
        _unesc = r'\R' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_s(self):
        _in        = '\S'
        _esc     = r'\\S'
        _unesc = r'\S' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_t(self):
        _in        = '\T'
        _esc     = r'\\T'
        _unesc = r'\T' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_u(self):
        _in        = '\U'
        _esc     = r'\\U'
        _unesc = r'\U' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_v(self):
        _in        = '\V'
        _esc     = r'\\V'
        _unesc = r'\V' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_w(self):
        _in        = '\W'
        _esc     = r'\\W'
        _unesc = r'\W' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_x(self):
        _in        = '\X'
        _esc     = r'\\X'
        _unesc = r'\X' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_y(self):
        _in        = '\Y'
        _esc     = r'\\Y'
        _unesc = r'\Y' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

    def testCase_z(self):
        _in        = '\Z'
        _esc     = r'\\Z'
        _unesc = r'\Z' 
        self.check_esc_unesc(_in,_esc,_unesc, 'k')

#
#######################
#

if __name__ == '__main__':
    unittest.main()

