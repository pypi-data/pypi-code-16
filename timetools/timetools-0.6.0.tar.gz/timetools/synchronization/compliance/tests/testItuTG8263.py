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

import matplotlib.pyplot as mpp
import unittest

import timetools.synchronization.clock as sc
import timetools.synchronization.oscillator as tso
import timetools.synchronization.oscillator.noise.gaussian as tsong
import timetools.synchronization.time as st

import timetools.synchronization.compliance.visualization as tscv

import timetools.synchronization.compliance.ituTG8263.compute as tscg8263
import timetools.synchronization.compliance.ituTG8263.wanderGeneration as tscg8263wg
import timetools.synchronization.compliance.ituTG8263.holdoverTransient as tscg8263h


class TestItuTG8263( unittest.TestCase ) :
    def testConstantTemperatureWanderGenerationMask( self ) :
        thisMask = tscg8263wg.constantTemperatureMtieNs

        figureHandle = mpp.figure( )
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 20e3) )
        mpp.ylim( (100, 200e3) )
        thisMask.addToPlot( figureHandle.number )

        mpp.yscale( 'log' )
        mpp.xscale( 'log' )
        mpp.grid( which = 'minor' )
        mpp.title( self.testConstantTemperatureWanderGenerationMask.__name__ )


    def testVariableTemperatureWanderGenerationMask( self ) :
        constTempMask = tscg8263wg.constantTemperatureMtieNs
        thisMask = tscg8263wg.variableTemperatureMtieNs

        figureHandle = mpp.figure( )
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 20e3) )
        mpp.ylim( (100, 200e3) )
        thisMask.addToPlot( figureHandle.number, color = 'b' )
        constTempMask.addToPlot( figureHandle.number, color = 'r', linestyle = '--' )

        mpp.yscale( 'log' )
        mpp.xscale( 'log' )
        mpp.grid( which = 'minor' )
        mpp.title( self.testVariableTemperatureWanderGenerationMask.__name__ )


    def testHoldoverTransientPhaseErrorMask( self ) :
        thisMask = tscg8263h.phaseErrorNs

        figureHandle = mpp.figure( )
        mpp.title( self.testHoldoverTransientPhaseErrorMask.__name__ )
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0, 100) )
        mpp.ylim( (-1000, 1000) )
        mpp.grid( )
        thisMask.addToPlot( figureHandle.number, linewidth = 4, color = 'b', marker = 'o' )

        mpp.grid( which = 'minor' )


    def testHoldoverTransientFfoMask( self ) :
        thisMask = tscg8263h.ffoPpb

        figureHandle = mpp.figure( )
        mpp.title( self.testHoldoverTransientFfoMask.__name__ )
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0, 24 * 3600) )
        mpp.ylim( (-15, 15) )
        mpp.grid( )
        thisMask.addToPlot( figureHandle.number, linewidth = 4, color = 'b', marker = 'o' )

        mpp.grid( which = 'minor' )


    def testHoldoverTransientFfoRateMask( self ) :
        thisMask = tscg8263h.ffoRatePpbPerSecond

        figureHandle = mpp.figure( )
        mpp.title( self.testHoldoverTransientFfoRateMask.__name__ )
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0, 3600) )
        mpp.ylim( (-2e-5, 2e-5) )
        mpp.grid( )
        thisMask.addToPlot( figureHandle.number, linewidth = 4, color = 'b', marker = 'o' )

        mpp.grid( which = 'minor' )


    def testWanderGenerationConstantTemperatureNs1( self ) :
        timeStepSeconds = 1
        numberSamples = 10000

        desiredNumberObservations = 15

        clockFfoPpb = 0.5
        clockRmsJitterPpb = 2

        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )

        clockModel = sc.ClockModel( tso.OscillatorModel( initialFfoPpb = clockFfoPpb,
                                                         noiseModel = tsong.GaussianNoise(
                                                             standardDeviationPpb = clockRmsJitterPpb,
                                                             seed = 1459 ) ) )
        localTimeSeconds, instantaneousLoFfoPpb = clockModel.generate( referenceTimeSeconds )

        analysisResult, thisMask, mtieData = tscg8263.analyzeItuTG8263Mask( localTimeSeconds, referenceTimeSeconds,
                                                                            timeStepSeconds, desiredNumberObservations )

        thisPlot = tscv.plot( )

        thisPlot.addMask( thisMask, linewidth = 4, color = 'r', linestyle = '--', marker = 'o' )
        thisPlot.addSignal( mtieData )

        thisPlot.go( )

        mpp.yscale( 'log' )
        mpp.xscale( 'log' )
        mpp.grid( which = 'minor' )
        mpp.title( self.testWanderGenerationConstantTemperatureNs1.__name__ )

        self.assertTrue( analysisResult, 'Failed 16 ppb mask when should not have' )


    def testWanderGenerationConstantTemperatureNs2( self ) :
        timeStepSeconds = 1
        numberSamples = 10000

        desiredNumberObservations = 15

        clockFfoPpb = 5
        clockRmsJitterPpb = 2

        referenceTimeGenerator = st.referenceGenerator( timeStepSeconds )
        referenceTimeSeconds = referenceTimeGenerator.generate( numberSamples )

        clockModel = sc.ClockModel( tso.OscillatorModel( initialFfoPpb = clockFfoPpb,
                                                         noiseModel = tsong.GaussianNoise(
                                                             standardDeviationPpb = clockRmsJitterPpb,
                                                             seed = 1459 ) ) )
        localTimeSeconds, instantaneousLoFfoPpb = clockModel.generate( referenceTimeSeconds )

        analysisResult, thisMask, mtieData = tscg8263.analyzeItuTG8263Mask( localTimeSeconds, referenceTimeSeconds,
                                                                            timeStepSeconds, desiredNumberObservations )

        thisPlot = tscv.plot( )

        thisPlot.addMask( thisMask, linewidth = 4, color = 'r', linestyle = '--' )
        thisPlot.addSignal( mtieData, linestyle = '--', marker = 'o' )

        thisPlot.go( )

        mpp.yscale( 'log' )
        mpp.xscale( 'log' )
        mpp.grid( which = 'minor' )
        mpp.title( self.testWanderGenerationConstantTemperatureNs2.__name__ )

        self.assertFalse( analysisResult, 'Passed 16 ppb mask when should not have' )


    def tearDown( self ) :
        if __name__ == "__main__" :
            mpp.show( )


if __name__ == "__main__" :
    unittest.main( )
