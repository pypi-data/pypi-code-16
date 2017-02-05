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
import time
import unittest

import timetools.signalProcessing.tolerance as spt
import timetools.synchronization.clock as sc
import timetools.synchronization.oscillator as tso
import timetools.synchronization.oscillator.noise.gaussian as tsong
import timetools.synchronization.time as st

import timetools.synchronization.analysis.ituTG810 as sag810
import timetools.synchronization.analysis.fastMtie as samtie


class TestMtie( unittest.TestCase ) :
    def testSingleProcessMtie( self ) :
        timeStepSeconds = 1 / 16
        numberSamples = 10000

        numberObservations = 5

        clockFfoPpb = 16
        clockRmsJitterPpb = 3.0

        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )

        clockModel = sc.ClockModel( tso.OscillatorModel( initialFfoPpb = clockFfoPpb,
                                                         noiseModel = tsong.GaussianNoise(
                                                             standardDeviationPpb = clockRmsJitterPpb,
                                                             seed = 1459 ) ) )

        localTimeSeconds, instantaneousLoFfoPpb = clockModel.generate( referenceTimeSeconds )

        directMtie, directObservationIntervals = sag810.calculateMtie( localTimeSeconds,
                                                                       referenceTimeSeconds,
                                                                       timeStepSeconds,
                                                                       numberObservations )
        # Test the single process MTIE calculation
        fastMtie, fastObservationIntervals = samtie.calculateMtie( localTimeSeconds,
                                                                   referenceTimeSeconds,
                                                                   timeStepSeconds,
                                                                   numberObservations,
                                                                   maximumNumberWorkers = 1 )

        self.assertTrue( len( directMtie ) == len( fastMtie ),
                         'MTIE data lengths not equal' )
        self.assertTrue( len( directObservationIntervals ) == len( fastObservationIntervals ),
                         'MTIE observation interval lengths not equal' )

        self.assertTrue( numpy.all( directObservationIntervals == fastObservationIntervals ),
                         'MTIE observations intervals not equal' )

        mtieTest = spt.ToleranceValue( directMtie, 0.1, spt.ToleranceUnit[ 'percent' ] )
        self.assertTrue( numpy.all( mtieTest.isWithinTolerance( fastMtie ) ),
                         'MTIE observations not equivalent' )


    def testMultiprocessMtie( self ) :
        timeStepSeconds = 1 / 16
        numberSamples = 10000

        numberObservations = 15

        clockFfoPpb = 16
        clockRmsJitterPpb = 3.0

        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )

        clockModel = sc.ClockModel( tso.OscillatorModel( initialFfoPpb = clockFfoPpb,
                                                         noiseModel = tsong.GaussianNoise(
                                                             standardDeviationPpb = clockRmsJitterPpb,
                                                             seed = 1459 ) ) )

        localTimeSeconds, instantaneousLoFfoPpb = clockModel.generate( referenceTimeSeconds )

        t1 = time.clock( )
        directMtie, directObservationIntervals = sag810.calculateMtie( localTimeSeconds,
                                                                       referenceTimeSeconds,
                                                                       timeStepSeconds,
                                                                       numberObservations )
        t = time.clock( ) - t1

        # Test the multiprocessing MTIE calculation
        ft1 = time.clock( )
        fastMtie, fastObservationIntervals = samtie.calculateMtie( localTimeSeconds,
                                                                   referenceTimeSeconds,
                                                                   timeStepSeconds,
                                                                   numberObservations, maximumNumberWorkers = 4 )
        ft = time.clock( ) - ft1

        self.assertTrue( (ft < t),
                         'Fast MTIE isn\'t fast: ' + str( t ) + ' (direct), ' + repr( ft ) + ' (fast)' )
        self.assertTrue( len( directMtie ) == len( fastMtie ),
                         'MTIE data lengths not equal' )
        self.assertTrue( len( directObservationIntervals ) == len( fastObservationIntervals ),
                         'MTIE observation interval lengths not equal' )

        self.assertTrue( numpy.all( directObservationIntervals == fastObservationIntervals ),
                         'MTIE observations intervals not equal' )

        mtieTest = spt.ToleranceValue( directMtie, 0.1, spt.ToleranceUnit[ 'percent' ] )
        self.assertTrue( numpy.all( mtieTest.isWithinTolerance( fastMtie ) ),
                         'MTIE observations not equivalent' )


if __name__ == "__main__" :
    unittest.main( )
