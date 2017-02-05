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

import timetools.synchronization.oscillator as tso
import timetools.synchronization.oscillator.aging as tsoa
import timetools.synchronization.oscillator.sensitivity as tsos


class TestClock( unittest.TestCase ) :
    def testOscillatorModel1( self ) :
        initialOffsetPpb = 10
        thisModel = tso.OscillatorModel( initialFfoPpb = initialOffsetPpb )

        referenceTimeSeconds = numpy.array( [ 1, 2, 3 ] )

        expectedFfoPpb = initialOffsetPpb * numpy.ones( referenceTimeSeconds.shape )

        actualFfoPpb = thisModel.generate( referenceTimeSeconds )

        self.assertTrue( numpy.all( actualFfoPpb == expectedFfoPpb ),
                         ("Unexpected FFO from oscillator model: "
                          + repr( actualFfoPpb ) + " (actual) "
                          + repr( expectedFfoPpb ) + " (expected)") )


    def testOscillatorModel2( self ) :
        initialOffsetPpb = 0
        thisAging = tsoa.LinearAging( 1, 0, 0 )

        thisModel = tso.OscillatorModel( initialFfoPpb = initialOffsetPpb, agingModel = thisAging )

        referenceTimeSeconds = 3600 * numpy.array( [ 0, 12, 24 ] )

        expectedFfoPpb = numpy.array( [ 0, 0.5, 1 ] )

        actualFfoPpb = thisModel.generate( referenceTimeSeconds )

        self.assertTrue( numpy.all( actualFfoPpb == expectedFfoPpb ),
                         ("Unexpected FFO from oscillator model: "
                          + repr( actualFfoPpb ) + " (actual) "
                          + repr( expectedFfoPpb ) + " (expected)") )


    def testOscillatorModel3( self ) :
        initialOffsetPpb = 0
        temperatureSensitivity = tsos.LinearTemperatureSensitivity( 1, 295 )

        thisModel = tso.OscillatorModel( initialFfoPpb = initialOffsetPpb,
                                         temperatureSensitivityModel = temperatureSensitivity )

        referenceTemperatureKelvin = numpy.array( [ 290, 295, 300 ] )

        referenceTimeSeconds = numpy.array( [ 1, 2, 3 ] )

        expectedFfoPpb = numpy.array( [ -5, 0, 5 ] )

        actualFfoPpb = thisModel.generate( referenceTimeSeconds,
                                           referenceTemperatureKelvin = referenceTemperatureKelvin )

        self.assertTrue( numpy.all( actualFfoPpb == expectedFfoPpb ),
                         ("Unexpected FFO from oscillator model: "
                          + repr( actualFfoPpb ) + " (actual) "
                          + repr( expectedFfoPpb ) + " (expected)") )


    def testOscillatorModel4( self ) :
        initialOffsetPpb = 0
        temperatureSensitivity = tsos.LinearTemperatureSensitivity( 1, 295 )
        thisAging = tsoa.LinearAging( 1, 0, 0 )

        thisModel = tso.OscillatorModel( initialFfoPpb = initialOffsetPpb, agingModel = thisAging,
                                         temperatureSensitivityModel = temperatureSensitivity )

        referenceTemperatureKelvin = numpy.array( [ 290, 295, 300 ] )

        referenceTimeSeconds = 3600 * numpy.array( [ 0, 12, 24 ] )

        expectedFfoPpb = numpy.array( [ -5, 0.5, 6 ] )

        actualFfoPpb = thisModel.generate( referenceTimeSeconds,
                                           referenceTemperatureKelvin = referenceTemperatureKelvin )

        self.assertTrue( numpy.all( actualFfoPpb == expectedFfoPpb ),
                         ("Unexpected FFO from oscillator model: "
                          + repr( actualFfoPpb ) + " (actual) "
                          + repr( expectedFfoPpb ) + " (expected)") )


if __name__ == "__main__" :
    unittest.main( )
