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

import timetools.synchronization.oscillator.aging as tsoa


class TestLinearAging( unittest.TestCase ) :
    def setUp(self):
        self.thisAging = tsoa.LinearAging( 1, 0, 0 )

    def testLinearAging1( self ) :
        expectedFfoPpb = 0

        actualFfoPpb = self.thisAging.generate( 0 )

        self.assertEqual( actualFfoPpb, expectedFfoPpb )


    def testLinearAging2( self ) :
        expectedFfoPpb = 1

        actualFfoPpb = self.thisAging.generate( 3600 * 24 )

        self.assertEqual( actualFfoPpb, expectedFfoPpb )


    def testLinearAging3( self ) :
        expectedFfoPpb = numpy.array( [ 0, 0.5, 1 ] )

        actualFfoPpb = self.thisAging.generate( 3600 * numpy.array( [ 0, 12, 24 ] ) )

        self.assertTrue( numpy.all( actualFfoPpb == expectedFfoPpb ),
                         ("Unexpected FFO from aging: "
                          + repr( actualFfoPpb ) + " (actual) "
                          + repr( expectedFfoPpb ) + " (expected)") )


if __name__ == '__main__' :
    unittest.main( )
