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

import timetools.synchronization.compliance.ituTG8262.eecOption1.wanderGeneration as tscg8262eec1wg
import timetools.synchronization.compliance.ituTG8262.eecOption1.wanderTolerance as tscg8262eec1wt
import timetools.synchronization.compliance.ituTG8262.eecOption2.wanderGeneration as tscg8262eec2wg
import timetools.synchronization.compliance.ituTG8262.eecOption2.wanderTolerance as tscg8262eec2wt
import timetools.synchronization.compliance.ituTG8262.jitterTolerance as tscg8262jt
import timetools.synchronization.compliance.ituTG8262.eecOption2.wanderTransfer as tscg8262eec2wtf
import timetools.synchronization.compliance.ituTG8262.eecOption2.transient as tscg8262eec2t
import timetools.synchronization.compliance.ituTG8262.eecOption1.holdover as tscg8262eec1h
import timetools.synchronization.compliance.ituTG8262.eecOption2.holdover as tscg8262eec2h
import timetools.synchronization.compliance.ituTG8262.eecOption2.noiseTransfer as tscg8262eec2nt
import timetools.synchronization.compliance.ituTG8262.eecOption2.frequencyAccuracy as tscg8262eec2fa
import timetools.synchronization.compliance.ituTG8262.eecOption1.frequencyAccuracy as tscg8262eec1fa
import timetools.synchronization.compliance.ituTG8262.eecOption2.phaseDiscontinuity as tscg8262eec2pd
import timetools.synchronization.compliance.ituTG8262.jitterGeneration as tscg8262jg


class TestItuTG8262 (unittest.TestCase):

    def testEec1MtieConstantTemperatureG8262WanderGenerationMask (self):
        thisMask = tscg8262eec1wg.mtieConstantTemperatureNs
          
        figureHandle = mpp.figure()
        mpp.title(self.testEec1MtieConstantTemperatureG8262WanderGenerationMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 1000) )
        mpp.ylim( (1, 1000) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
         
 
    def testEec1MtieVariableTemperatureG8262WanderGenerationMask (self):
        constantTempMask = tscg8262eec1wg.mtieConstantTemperatureNs
        thisMask = tscg8262eec1wg.mtieTemperatureNs
         
        figureHandle = mpp.figure()
        mpp.title(self.testEec1MtieVariableTemperatureG8262WanderGenerationMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 1000) )
        mpp.ylim( (1, 1000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        constantTempMask.addToPlot(figureHandle.number, color='b')
         
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec1TdevConstantTemperatureG8262WanderGenerationMask (self):
        thisMask = tscg8262eec1wg.tdevConstantTemperatureNs
        
        figureHandle = mpp.figure()
        mpp.title(self.testEec1TdevConstantTemperatureG8262WanderGenerationMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 1000) )
        mpp.ylim( (0.1, 100) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec1MtieConstantTemperatureG8262WanderToleranceMask (self):
        thisMask = tscg8262eec1wt.mtieMicroseconds
        
        figureHandle = mpp.figure()
        mpp.title(self.testEec1MtieConstantTemperatureG8262WanderToleranceMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 1000) )
        mpp.ylim( (0.1, 10) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec1TdevConstantTemperatureG8262WanderToleranceMask (self):
        thisMask = tscg8262eec1wt.tdevNs
        
        figureHandle = mpp.figure()
        mpp.title(self.testEec1TdevConstantTemperatureG8262WanderToleranceMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 1000) )
        mpp.ylim( (1, 1000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec2MtieConstantTemperatureG8262WanderGenerationMask (self):
        thisMask = tscg8262eec2wg.mtieConstantTemperatureNs
          
        figureHandle = mpp.figure()
        mpp.title(self.testEec2MtieConstantTemperatureG8262WanderGenerationMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 1000) )
        mpp.ylim( (1, 1000) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec2TdevConstantTemperatureG8262WanderGenerationMask (self):
        thisMask = tscg8262eec2wg.tdevConstantTemperatureNs
        
        figureHandle = mpp.figure()
        mpp.title(self.testEec2TdevConstantTemperatureG8262WanderGenerationMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 10000) )
        mpp.ylim( (0.1, 100) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec2TdevG8262WanderToleranceMask (self):
        thisMask = tscg8262eec2wt.tdevNs
        
        figureHandle = mpp.figure()
        mpp.title(self.testEec2TdevG8262WanderToleranceMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 1000) )
        mpp.ylim( (1, 1000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testG8262JitterTolerance1GMask (self):
        thisMask = tscg8262jt.jitterAmplitude1G
        
        figureHandle = mpp.figure()
        mpp.title(self.testG8262JitterTolerance1GMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (10, 1000000) )
        mpp.ylim( (0.1, 1000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testG8262JitterTolerance10GMask (self):
        thisMask = tscg8262jt.jitterAmplitude10G
        
        figureHandle = mpp.figure()
        mpp.title(self.testG8262JitterTolerance10GMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (10, 1000000) )
        mpp.ylim( (0.1, 10000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec2TdevG8262WanderTransferMask (self):
        thisMask = tscg8262eec2wtf.tdevNs
        
        figureHandle = mpp.figure()
        mpp.title(self.testEec2TdevG8262WanderTransferMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 1000) )
        mpp.ylim( (1, 1000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec2MtieTransientMask (self):
        thisMask = tscg8262eec2t.transientMtieNs
          
        figureHandle = mpp.figure()
        mpp.title(self.testEec2MtieTransientMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.014, 10) )
        mpp.ylim( (10, 1000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec1HoldoverPhaseErrorMask (self):
        thisMask = tscg8262eec1h.phaseErrorNs
          
        figureHandle = mpp.figure()
        mpp.title(self.testEec1HoldoverPhaseErrorMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 10000) )
        mpp.ylim( (-10e6, 10e6) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
          
        mpp.xscale('symlog')
        mpp.yscale('symlog')
        mpp.grid()
        

    def testEec2HoldoverPhaseErrorMask (self):
        thisMask = tscg8262eec2h.phaseErrorNs
          
        figureHandle = mpp.figure()
        mpp.title(self.testEec2HoldoverPhaseErrorMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 10000) )
        mpp.ylim( (-10e6, 10e6) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.xscale('symlog')
        mpp.yscale('symlog')
        mpp.grid()
        
        
    def testEec1SinusoidalWanderMask (self):
        thisMask = tscg8262eec1wt.generateSinusoidalMask()
          
        figureHandle = mpp.figure()
        mpp.title(self.testEec1SinusoidalWanderMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1e-3, 10) )
        mpp.ylim( (0.1, 6) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.xscale('log')
        mpp.yscale('log')
        mpp.grid(which='minor')
        

    def testEec2TdevNoiseTransferMask (self):
        thisMask = tscg8262eec2nt.tdevNs
        
        figureHandle = mpp.figure()
        mpp.title(self.testEec2TdevNoiseTransferMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 1000) )
        mpp.ylim( (1, 10000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def testEec2FrequencyAccuracyMask (self):
        thisMask = tscg8262eec2fa.ffoPpm
        
        figureHandle = mpp.figure()
        
        mpp.title(self.testEec2FrequencyAccuracyMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, (24.0 * 3600 * 365)) )
        mpp.ylim( (-5.0, 5.0) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r', marker='o')
        
        mpp.xscale('symlog')
        mpp.grid(which='minor')
        

    def testEec1FrequencyAccuracyMask (self):
        thisMask = tscg8262eec1fa.generateFfoMask()
        
        figureHandle = mpp.figure()
        
        mpp.title(self.testEec1FrequencyAccuracyMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, (24.0 * 3600 * 365)) )
        mpp.ylim( (-5.0, 5.0) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r', marker='o')
        
        mpp.xscale('symlog')
        mpp.grid(which='minor')
        

    def testEec2TdevPhaseDiscontinuityMask (self):
        thisMask = tscg8262eec2pd.mtieNs
        
        figureHandle = mpp.figure()
        mpp.title(self.testEec2TdevPhaseDiscontinuityMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.014, 1000) )
        mpp.ylim( (10, 1000) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        
        
    def testJitterGeneration1GMask (self):
        thisMask = tscg8262jg.amplitude1G
        
        figureHandle = mpp.figure()
        mpp.title(self.testJitterGeneration1GMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (1e3, 15e6) )
        mpp.ylim( (0, 1) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        
        
    def testJitterGeneration10GMask (self):
        thisMask = tscg8262jg.amplitude10G
        
        figureHandle = mpp.figure()
        mpp.title(self.testJitterGeneration10GMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (1e3, 100e6) )
        mpp.ylim( (0, 1) )
        thisMask.addToPlot(figureHandle.number, linewidth=3, color='r')
        
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def tearDown (self):
        if __name__ == "__main__":
            mpp.show()


if __name__ == "__main__":
    unittest.main()
    