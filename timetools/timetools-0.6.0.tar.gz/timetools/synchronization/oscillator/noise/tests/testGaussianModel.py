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

import timetools.signalProcessing.tolerance as tspt
import timetools.synchronization.oscillator.noise.gaussian as tsong


class TestGaussianModel( unittest.TestCase ) :
    def testNoiseModel1( self ) :
        thisNoiseModel = tsong.GaussianNoise( seed = 31415 )

        expectedFfoPpb = numpy.array( [ 1.36242188, 1.13410818, 2.36307449 ] )

        actualFfoPpb = thisNoiseModel.generate( numpy.array( [ 1, 2, 3 ] ) )

        thisTolerance = tspt.ToleranceValue( expectedFfoPpb, 1e-6, tspt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( thisTolerance.isWithinTolerance( actualFfoPpb ),
                         ('Result not wihin tolerance '
                          + repr( actualFfoPpb ) + ' (actual) '
                          + repr( expectedFfoPpb ) + ' (expected)') )


if __name__ == '__main__' :
    unittest.main( )
