'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2015-11-28

This file is part of StruPy.
StruPy is a structural engineering design Python package.
http://strupy.org/

StruPy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

StruPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
File version 0.2 changes:
- RcSteelClass data structure changed
- get_availablercsteelclass() added
'''

import strupy.units as u
from Bolt_PN import Bolt_PN

class BoltConnect_PN (Bolt_PN):

    def __init__(self):
        print "BoltConnect_PN init"
        Bolt_PN.__init__(self)
        self.fd = 310 * u.MPa
        self.t1 = 6 * u.mm
        self.t2 = 6 * u.mm
        self.a = 40.0 * u.mm
        self.a1 = 40.0 * u.mm
        self.m = 1.0
        self.mi = 0.1
        #---
        self.SRb = self.As * self.Rm
        self.SRs = self.As * self.Rm       
        #---  
        
    def _calculateconnect(self):
        self._calculatebolt()
        #---SRb
        alfa = min (self.a1 / self.d, self.a/self.d - 0.75 , 2.5)
        print alfa
        sum_t = min (self.t1, self.t2)
        print sum_t
        self.SRb = alfa * self.fd * self.d * sum_t
        self.SRb = self.SRb.asUnit(u.kN)
        print self.SRb
        #---SRs
        alfa_s = 1
        Si = 0 * u.kN
        self.SRs =   alfa_s * self.mi * (self.SRt - Si) * self.m
        self.SRs = self.SRs.asUnit(u.kN)
        print self.SRs

# Test if main
if __name__ == '__main__':
    print ('test BoltConnect')
    connect = BoltConnect_PN()
    #print vars(connect)
    #print vars(connect)
    connect.set_BoltDim('M20')
    print connect.Dim
    print connect.Grade
    connect._calculateconnect()
    print 'SRt =' + str(connect.SRt)
    print 'SRv =' + str(connect.SRv)
    print 'SRr =' + str(connect.SRr)
    print 'SRrdyn =' + str(connect.SRrdyn)
    print 'SRb =' + str(connect.SRb)
    print 'SRs =' + str(connect.SRs) 

     
     
     
    
