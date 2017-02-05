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
import timetools.synchronization.clock as sc
import timetools.synchronization.oscillator as tso
import timetools.synchronization.oscillator.noise.gaussian as tsong
import timetools.synchronization.time as st

import timetools.synchronization.analysis.ituTG810 as sag810
import timetools.synchronization.analysis.fastTdev as satdev


class TestTdev( unittest.TestCase ) :
    def testDirectTdev( self ) :
        timeStepSeconds = 1 / 16
        referenceTimeSeconds = numpy.arange( 0, 9 )
        timeError = numpy.array( [ 1, 0, 4, 2, 5, 1, 4, 0, 3 ] )
        expectedTdev = numpy.array( [ 2.591193879, 0.7499999999, 0.5443310541 ] )

        numberObservations = 3

        localTimeSeconds = referenceTimeSeconds + timeError

        directTdev, directObservationIntervals = sag810.calculateTdev( localTimeSeconds,
                                                                       referenceTimeSeconds,
                                                                       timeStepSeconds,
                                                                       numberObservations )

        self.assertTrue( len( directObservationIntervals ) == numberObservations, 'Incorrect number of observations' )
        self.assertTrue( len( directObservationIntervals ) == len( directTdev ), 'Mismatched TDEV and observations' )

        tdevTest = spt.ToleranceValue( expectedTdev, 1e-9, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( numpy.all( tdevTest.isWithinTolerance( directTdev ) ), 'TDEV observations not equivalent' )


    def testSingleProcesTdev1( self ) :
        timeStepSeconds = 1 / 16
        referenceTimeSeconds = numpy.arange( 0, 9 )
        timeError = numpy.array( [ 1, 0, 4, 2, 5, 1, 4, 0, 3 ] )
        expectedTdev = numpy.array( [ 2.591193879, 0.7499999999, 0.5443310541 ] )

        numberObservations = 3

        localTimeSeconds = referenceTimeSeconds + timeError

        directTdev, directObservationIntervals = sag810.calculateTdev( localTimeSeconds,
                                                                       referenceTimeSeconds,
                                                                       timeStepSeconds,
                                                                       numberObservations )
        fastTdev, fastObservationIntervals = satdev.calculateTdev( localTimeSeconds,
                                                                   referenceTimeSeconds,
                                                                   timeStepSeconds,
                                                                   numberObservations,
                                                                   maximumNumberWorkers = 1 )

        self.assertTrue( len( directTdev ) == len( fastTdev ), 'TDEV data lengths not equal' )
        self.assertTrue( len( directObservationIntervals ) == len( fastObservationIntervals ),
                         'TDEV observation interval lengths not equal' )

        self.assertTrue( numpy.all( directObservationIntervals == fastObservationIntervals ),
                         'TDEV observations intervals not equal' )

        tdevTest1 = spt.ToleranceValue( directTdev, 1e-9, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( numpy.all( tdevTest1.isWithinTolerance( fastTdev ) ), 'TDEV observations not equivalent' )
        tdevTest2 = spt.ToleranceValue( expectedTdev, 1e-9, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( numpy.all( tdevTest2.isWithinTolerance( fastTdev ) ), 'fast TDEV observations not equivalent' )


    def testSingleprocessTdev2( self ) :
        timeStepSeconds = 1 / 16
        numberSamples = 1000

        numberObservations = 15

        clockFfoPpb = 16
        clockRmsJitterPpb = 3

        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )

        clockModel = sc.ClockModel( tso.OscillatorModel( initialFfoPpb = clockFfoPpb,
                                                         noiseModel = tsong.GaussianNoise(
                                                             standardDeviationPpb = clockRmsJitterPpb,
                                                             seed = 1459 ) ) )

        localTimeSeconds, instantaneousLoFfoPpb = clockModel.generate( referenceTimeSeconds )

        directTdev, directObservationIntervals = sag810.calculateTdev( localTimeSeconds,
                                                                       referenceTimeSeconds,
                                                                       timeStepSeconds,
                                                                       numberObservations )
        fastTdev, fastObservationIntervals = satdev.calculateTdev( localTimeSeconds,
                                                                   referenceTimeSeconds,
                                                                   timeStepSeconds,
                                                                   numberObservations,
                                                                   maximumNumberWorkers = 1 )

        self.assertTrue( len( directTdev ) == len( fastTdev ), 'TDEV data lengths not equal' )
        self.assertTrue( len( directObservationIntervals ) == len( fastObservationIntervals ),
                         'TDEV observation interval lengths not equal' )

        self.assertTrue( numpy.all( directObservationIntervals == fastObservationIntervals ),
                         'TDEV observations intervals not equal' )

        tdevTest = spt.ToleranceValue( directTdev, 1e-9, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( numpy.all( tdevTest.isWithinTolerance( fastTdev ) ), 'TDEV observations not equivalent' )


    def testMultiprocessTdev( self ) :
        timeStepSeconds = 1 / 16
        numberSamples = 1000

        numberObservations = 15

        clockFfoPpb = 16
        clockRmsJitterPpb = 3

        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )

        clockModel = sc.ClockModel( tso.OscillatorModel( initialFfoPpb = clockFfoPpb,
                                                         noiseModel = tsong.GaussianNoise(
                                                             standardDeviationPpb = clockRmsJitterPpb,
                                                             seed = 1459 ) ) )

        localTimeSeconds, instantaneousLoFfoPpb = clockModel.generate( referenceTimeSeconds )

        directTdev, directObservationIntervals = sag810.calculateTdev( localTimeSeconds,
                                                                       referenceTimeSeconds,
                                                                       timeStepSeconds,
                                                                       numberObservations )
        fastTdev, fastObservationIntervals = satdev.calculateTdev( localTimeSeconds,
                                                                   referenceTimeSeconds,
                                                                   timeStepSeconds,
                                                                   numberObservations )

        self.assertTrue( len( directTdev ) == len( fastTdev ), 'TDEV data lengths not equal' )
        self.assertTrue( len( directObservationIntervals ) == len( fastObservationIntervals ),
                         'TDEV observation interval lengths not equal' )

        self.assertTrue( numpy.all( directObservationIntervals == fastObservationIntervals ),
                         'TDEV observations intervals not equal' )

        tdevTest = spt.ToleranceValue( directTdev, 0.1, spt.ToleranceUnit[ 'percent' ] )
        self.assertTrue( numpy.all( tdevTest.isWithinTolerance( fastTdev ) ), 'TDEV observations not equivalent' )


    def testDirectTvar( self ) :
        timeStepSeconds = 1 / 16
        referenceTimeSeconds = numpy.arange( 0, 9 )
        timeError = numpy.array( [ 1, 0, 4, 2, 5, 1, 4, 0, 3 ] )
        expectedTvar = numpy.power( numpy.array( [ 2.591193879, 0.7499999999, 0.5443310541 ] ), 2 )

        numberObservations = 3

        localTimeSeconds = referenceTimeSeconds + timeError

        directTvar, directObservationIntervals = sag810.calculateTvar( localTimeSeconds,
                                                                       referenceTimeSeconds,
                                                                       timeStepSeconds,
                                                                       numberObservations )

        self.assertTrue( len( directObservationIntervals ) == numberObservations,
                         'Incorrect number of TVAR observations' )
        self.assertTrue( len( directObservationIntervals ) == len( directTvar ), 'Mismatched TVAR and observations' )

        tvarTest = spt.ToleranceValue( expectedTvar, 1e-8, spt.ToleranceUnit[ 'relative' ] )
        self.assertTrue( numpy.all( tvarTest.isWithinTolerance( directTvar ) ), 'TVAR observations not equivalent' )


if __name__ == "__main__" :
    unittest.main( )
