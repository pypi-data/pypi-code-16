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

import timetools.synchronization.oscillator.sensitivity as tsos


class TestLinearTemperatureSensitivity( unittest.TestCase ) :
    def setUp( self ) :
        self.temperatureSensitivity = tsos.LinearTemperatureSensitivity( 1, 295 )


    def testTemperatureSensitivity1( self ) :
        expectedFfoPpb = 0

        actualFfoPpb = self.temperatureSensitivity.generate( 295 )

        self.assertEqual( actualFfoPpb, expectedFfoPpb )


    def testTemperatureSensitivity2( self ) :
        expectedFfoPpb = 5

        actualFfoPpb = self.temperatureSensitivity.generate( 300 )

        self.assertEqual( actualFfoPpb, expectedFfoPpb )


    def testTemperatureSensitivity3( self ) :
        expectedFfoPpb = numpy.array( [ -5, 0, 5 ] )

        actualFfoPpb = self.temperatureSensitivity.generate( numpy.array( [ 290, 295, 300 ] ) )

        self.assertTrue( numpy.all( actualFfoPpb == expectedFfoPpb ),
                         ("Unexpected FFO from temperature sensitivity: "
                          + repr( actualFfoPpb ) + " (actual) "
                          + repr( expectedFfoPpb ) + " (expected)") )


if __name__ == '__main__' :
    unittest.main( )
