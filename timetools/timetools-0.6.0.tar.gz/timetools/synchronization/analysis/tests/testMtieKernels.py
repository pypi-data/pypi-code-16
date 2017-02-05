#
# Copyright 2017 Russell Smiley
#
# This file is part of timetools.
#
# timetools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# timetools is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with timetools.  If not, see <http://www.gnu.org/licenses/>.
#

import numpy
import unittest

import timetools.signalProcessing.tolerance as spt

import timetools.synchronization.analysis.mtieKernels as tsam


class TestMtieKernels( unittest.TestCase ):

    def testSlidingWindow( self ):
        expectedMtie = 1.8508331568
        
        timebase = numpy.linspace( 0, ( 2 * numpy.pi ), 10 )
        signal = numpy.sin( timebase )

        actualMtie = tsam.slidingWindow( signal, 4 )

        thisTolerance = spt.ToleranceValue( expectedMtie, 1e-11, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( thisTolerance.isWithinTolerance( actualMtie ), 
                         'Unexpected MTIE result: ' + str( expectedMtie ) + ' (expected), ' 
                         + str( actualMtie ) + ' (actual)' )
        

    def testSmartWindow( self ):
        expectedMtie = 1.8508331568
        
        timebase = numpy.linspace( 0, ( 2 * numpy.pi ), 10 )
        signal = numpy.sin( timebase )

        actualMtie = tsam.smartWindow( signal, 4 )

        thisTolerance = spt.ToleranceValue( expectedMtie, 1e-11, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( thisTolerance.isWithinTolerance( actualMtie ), 
                        'Unexpected MTIE result: ' + str( expectedMtie ) + ' (expected), ' 
                         + str( actualMtie ) + ' (actual)' )


if __name__ == "__main__":
    unittest.main()
    