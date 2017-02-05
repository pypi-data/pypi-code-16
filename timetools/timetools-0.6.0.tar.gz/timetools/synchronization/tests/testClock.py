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

import timetools.synchronization.analysis.ituTG810 as sag810
import timetools.synchronization.oscillator as tso
import timetools.synchronization.oscillator.noise.gaussian as tsong
import timetools.synchronization.time as st
import timetools.signalProcessing.tolerance as spt

import timetools.synchronization.clock as tsc


class TestClock( unittest.TestCase ):

    def testCalculateLocalTimeFromFfo1( self ):
        referenceTimeSeconds = numpy.array( [ 1, 2, 3 ] )
        ffoPpb = numpy.array( [ 3, -6, 9 ] ) * 1e8

        expectedLocalTimeSeconds = numpy.array( [ 1, 2.3, 2.7 ] )
        actualLocalTimeSeconds = tsc.calculateLocalTimeFromFfo( referenceTimeSeconds, ffoPpb )

        thisTolerance = spt.ToleranceValue( expectedLocalTimeSeconds, 1e-6, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( thisTolerance.isWithinTolerance( actualLocalTimeSeconds ),
                         ( "Unexpected local time: "
                           + repr( actualLocalTimeSeconds ) + " (actual) "
                           + repr( expectedLocalTimeSeconds ) + " (expected)" ) )

    def testCalculateLocalTimeFromFfo2( self ):
        initialConditions = [ numpy.array( [ 0, 0, 0 ] ) , numpy.array( [ 9*1e8, 3, 2.7 ] ) ]
        referenceTimeSeconds = [ numpy.array( [ 1, 2, 3 ] ), numpy.array( [ 4, 5, 6, 7 ] ) ]
        ffoPpb = [ numpy.array( [ 3, -6, 9 ] ) * 1e8, numpy.array( [ 1, -2, 4, 0 ] ) * 1e8 ]

        expectedLocalTimeSeconds = [ numpy.array( [ 1, 2.3, 2.7 ] ), numpy.array( [ 4.6, 5.7, 6.5, 7.9 ] ) ]

        concatenatedReferenceTimeSeconds = numpy.concatenate( ( referenceTimeSeconds[0], referenceTimeSeconds[1] ) )
        concatenatedFfoPpb = numpy.concatenate( ( ffoPpb[0], ffoPpb[1] ) )
        concatenatedExpectedLocalTimeSeconds = numpy.concatenate( ( expectedLocalTimeSeconds[0], expectedLocalTimeSeconds[1] ) )
        actualConcatenatedLocalTimeSeconds = \
            tsc.calculateLocalTimeFromFfo(
                concatenatedReferenceTimeSeconds,
                concatenatedFfoPpb,
                initialConditions[0][0],
                initialConditions[0][1],
                initialConditions[0][2] )

        concatenatedTolerance = spt.ToleranceValue( concatenatedExpectedLocalTimeSeconds, 1e-6, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( concatenatedTolerance.isWithinTolerance( actualConcatenatedLocalTimeSeconds ),
                         ( "Unexpected concatenated local time: "
                           + repr( actualConcatenatedLocalTimeSeconds ) + " (actual) "
                           + repr( concatenatedExpectedLocalTimeSeconds ) + " (expected)" ) )

        for i in range(2):
            actualLocalTimeSeconds = \
                tsc.calculateLocalTimeFromFfo(
                    referenceTimeSeconds[i],
                    ffoPpb[i],
                    initialConditions[i][0],
                    initialConditions[i][1],
                    initialConditions[i][2] )

            thisTolerance = spt.ToleranceValue( expectedLocalTimeSeconds[i], 1e-6, spt.ToleranceUnit[ 'relative' ] )
            self.assertTrue( thisTolerance.isWithinTolerance( actualLocalTimeSeconds ),
                             ( "Unexpected local time (" + repr(i) + "): "
                               + repr( actualLocalTimeSeconds ) + " (actual) "
                               + repr( expectedLocalTimeSeconds[i] ) + " (expected)" ) )


    def testClock1( self ):
        timeStepSeconds = 1 / 16
        numberSamples = 10
        
        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )
        
        clockModel = tsc.ClockModel( tso.OscillatorModel( ) )
        
        localTimeSeconds, instantaneousLoFfoPpb = clockModel.generate( referenceTimeSeconds )
        
        self.assertTrue( numpy.all( localTimeSeconds == referenceTimeSeconds ), 'Timebases not equivalent' )
        self.assertTrue( numpy.all( instantaneousLoFfoPpb == 0 ), 'Instantaneous FFO not zero' )


    def testClock2( self ):
        timeStepSeconds = 1 / 16
        numberSamples = 10
        
        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )
        
        clockModel = tsc.ClockModel( tso.OscillatorModel( ) )
        
        localTimeSeconds = numpy.array([])
        instantaneousLoFfoPpb = numpy.array([])
        for thisTime in referenceTimeSeconds:
            thisLocalTimeSeconds, thisInstantaneousLoFfoPpb = clockModel.generate( numpy.array( [ thisTime ] ) )
            localTimeSeconds = numpy.concatenate( ( localTimeSeconds, thisLocalTimeSeconds ) )
            instantaneousLoFfoPpb = numpy.concatenate( ( instantaneousLoFfoPpb, thisInstantaneousLoFfoPpb ) )
        
        self.assertTrue( numpy.all( localTimeSeconds == referenceTimeSeconds ), 'Timebases not equivalent' )
        self.assertTrue( numpy.all( instantaneousLoFfoPpb == 0 ), 'Instantaneous FFO not zero' )


    def testClock3( self ):
        timeStepSeconds = 1 / 16
        numberSamples = 10
        
        initialFfoPpb = 100e3
        
        expectedLocalTimeSeconds = numpy.array( [ 0.0, 0.06250625, 0.1250125, 0.18751875, 0.250025, 0.31253125,
                                                0.3750375, 0.43754375, 0.50005, 0.56255625] )
        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )
        
        expectedTimeErrorSeconds = sag810.calculateTimeError( expectedLocalTimeSeconds, referenceTimeSeconds )
        
        clockModel = tsc.ClockModel( tso.OscillatorModel( initialFfoPpb = initialFfoPpb ) )
        
        actualLocalTimeSeconds, instantaneousLoFfoPpb = clockModel.generate( referenceTimeSeconds )
        actualTimeErrorSeconds = sag810.calculateTimeError( actualLocalTimeSeconds, referenceTimeSeconds )
        
        self.assertTrue( numpy.all( instantaneousLoFfoPpb == initialFfoPpb),
                         ( 'Unexpected FFO: '
                           + repr( instantaneousLoFfoPpb ) + ' (actual) '
                           + repr( numpy.ones( instantaneousLoFfoPpb.shape ) * initialFfoPpb ) + ' (expected)' ) )
        thisTolerance = spt.ToleranceValue( expectedTimeErrorSeconds, 1e-6, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( numpy.all( thisTolerance.isWithinTolerance( actualTimeErrorSeconds ) ),
                         'Timebases not equivalent' )


    def testClock4( self ):
        timeStepSeconds = 1 / 16
        numberSamples = 10

        initialFfoPpb = 100e3

        expectedLocalTimeSeconds = numpy.array( [ 0.0, 0.06250625, 0.1250125, 0.18751875, 0.250025, 0.31253125,
                                                0.3750375, 0.43754375, 0.50005, 0.56255625] )
        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )

        expectedTimeErrorSeconds = sag810.calculateTimeError( expectedLocalTimeSeconds, referenceTimeSeconds )

        clockModel = tsc.ClockModel( tso.OscillatorModel( initialFfoPpb = initialFfoPpb ) )

        actualLocalTimeSeconds = numpy.array( [] )
        instantaneousLoFfoPpb = numpy.array( [] )
        for i in range(0, 2):
            thisIterationReferenceTimeSeconds = referenceTimeSeconds[:5]
            if i == 1:
                thisIterationReferenceTimeSeconds = referenceTimeSeconds[5:]

            thisIterationActualLocalTimeSeconds, thisIterationInstantaneousLoFfoPpb = \
                clockModel.generate( thisIterationReferenceTimeSeconds )

            actualLocalTimeSeconds = numpy.concatenate( ( actualLocalTimeSeconds, thisIterationActualLocalTimeSeconds ) )
            instantaneousLoFfoPpb = numpy.concatenate( ( instantaneousLoFfoPpb, thisIterationInstantaneousLoFfoPpb ) )

        actualTimeErrorSeconds = sag810.calculateTimeError( actualLocalTimeSeconds, referenceTimeSeconds )

        self.assertTrue( numpy.all( instantaneousLoFfoPpb == initialFfoPpb),
                         ( 'Unexpected FFO: '
                           + repr( instantaneousLoFfoPpb ) + ' (actual) '
                           + repr( numpy.ones( instantaneousLoFfoPpb.shape ) * initialFfoPpb ) + ' (expected)' ) )
        thisTolerance = spt.ToleranceValue( expectedTimeErrorSeconds, 1e-6, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( numpy.all( thisTolerance.isWithinTolerance( actualTimeErrorSeconds ) ),
                         'Timebases not equivalent' )


    def testClockRandomSeed( self ):
        timeStepSeconds = 1 / 16
        numberSamples = 10
        
        initialFfoPpb = 100e3
        rmsJitterPpb = 3.0
        
        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )
        
        # Two models with the same seed should generate the exact same sequence
        clockModel1 = tsc.ClockModel(
            tso.OscillatorModel( initialFfoPpb = initialFfoPpb,
                                 noiseModel = tsong.GaussianNoise( seed = 1459 ) ) )
        clockModel2 = tsc.ClockModel(
            tso.OscillatorModel( initialFfoPpb = initialFfoPpb,
                                 noiseModel = tsong.GaussianNoise( seed = 1459 ) ) )
        clockModel3 = tsc.ClockModel(
            tso.OscillatorModel( initialFfoPpb = initialFfoPpb,
                                 noiseModel = tsong.GaussianNoise( seed = 5986 ) ) )
        
        actualLocalTimeSeconds1, instantaneousLoFfoPpb1 = clockModel1.generate( referenceTimeSeconds )
        actualLocalTimeSeconds2, instantaneousLoFfoPpb2 = clockModel2.generate( referenceTimeSeconds )
        actualLocalTimeSeconds3, instantaneousLoFfoPpb3 = clockModel3.generate( referenceTimeSeconds )
        
        self.assertTrue( numpy.all( instantaneousLoFfoPpb1 == instantaneousLoFfoPpb2 ),
                         'Instantaneous FFO with identical seed not the same' )
        self.assertFalse( numpy.all( instantaneousLoFfoPpb1 == instantaneousLoFfoPpb3 ),
                          'Instantaneous FFO with different seed is the same' )
        self.assertTrue( numpy.all( actualLocalTimeSeconds1 == actualLocalTimeSeconds2 ),
                         'Timebases with identical seed not the same' )
        self.assertFalse( numpy.all( actualLocalTimeSeconds1 == actualLocalTimeSeconds3 ),
                          'Timebases with identical seed is the same' )


if __name__ == "__main__":
    unittest.main()
    