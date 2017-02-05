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
import math
import unittest

import timetools.pdv.generator.general as tpgg
import timetools.pdv.generator.parameters as tpgp
from timetools.synchronization.compliance.general import createSimpleThresholdMask


class TestGenerator (unittest.TestCase):
    
    def setUp(self):
        self._numberSamples = 1000
        self._mean = 5
        self._standardDeviation = 2
        
        unittest.TestCase.setUp(self)
        
    
    def testGenerateGaussian1 (self):
        clipThresholds = ( 9, 1 )
        
        parameters = tpgp.GaussianParameters()
        parameters.mean = self._mean
        parameters.standardDeviation = self._standardDeviation
        parameters.upperThreshold = clipThresholds[0]
        parameters.lowerThreshold = clipThresholds[1]
        
        thisMask = createSimpleThresholdMask(clipThresholds[0], 0, lowerThreshold = clipThresholds[1])
        thisGenerator = tpgg.Gaussian(parameters)
        
        data = thisGenerator.generate(numpy.arange(0, self._numberSamples))
        
        result = thisMask.evaluate((numpy.arange(0, len(data)), data))
        
        self.assertTrue(result, 'Clipped Gaussian mask failed')
        
        
    def testGeneratePredefined1 (self):
        pdvData = numpy.random.normal(1, 3, self._numberSamples)
        thisGenerator = tpgg.Predefined(pdvData)

        timebase = numpy.arange(0, 100)
        
        newData = thisGenerator.generate(timebase)
        
        self.assertTrue(numpy.all(newData == pdvData[timebase]), 'Failed to select data subsequence')
        
        
    def testGeneratePredefined2 (self):
        pdvData = numpy.random.normal(1, 3, self._numberSamples)
        thisGenerator = tpgg.Predefined(pdvData)

        timebase = numpy.arange(0, (self._numberSamples + 100))
        
        newData = thisGenerator.generate(timebase)
        
        concatenatedExpectedSequence = numpy.concatenate( (pdvData, pdvData) )
        
        self.assertTrue(numpy.all(newData == concatenatedExpectedSequence[timebase]), 'Failed to concatenate data')
        
        
    def testGeneratePredefined3 (self):
        pdvData = numpy.random.normal(1, 3, self._numberSamples)
        thisGenerator = tpgg.Predefined(pdvData)

        timebase1 = numpy.arange(0, math.floor(self._numberSamples / 3))
        timebase2 = numpy.arange(0, self._numberSamples) + len(timebase1)
        
        newData1 = thisGenerator.generate(timebase1)
        newData2 = thisGenerator.generate(timebase2)
        
        concatenatedTimebase = numpy.concatenate( (timebase1, timebase2) )
        concatenatedExpectedSequence = numpy.concatenate( (pdvData, pdvData) )
        
        concatenatedNewData = numpy.concatenate( (newData1, newData2) )
        
        self.assertTrue(numpy.all(concatenatedNewData == concatenatedExpectedSequence[concatenatedTimebase]), 'Failed to iterate over data')
    
    
    def testGenerateUniform1 (self):
        clipThresholds = ( 9, 1 )
        
        parameters = tpgp.UniformParameters()
        parameters.upperThreshold = clipThresholds[0]
        parameters.lowerThreshold = clipThresholds[1]
        
        thisMask = createSimpleThresholdMask(clipThresholds[0], 0, lowerThreshold = clipThresholds[1])
        thisGenerator = tpgg.Uniform(parameters)
        
        data = thisGenerator.generate(numpy.arange(0, self._numberSamples))
        
        result = thisMask.evaluate((numpy.arange(0, len(data)), data))
        
        self.assertTrue(result, 'Uniform mask failed')
    
    
    def testGenerateExponential1 (self):
        clipThreshold = 9
        
        parameters = tpgp.ExponentialParameters()
        parameters.offset = 2
        parameters.scale = 3
        parameters.upperThreshold = clipThreshold
        
        thisMask = createSimpleThresholdMask(clipThreshold, 0, lowerThreshold = parameters.offset)
        thisGenerator = tpgg.Exponential(parameters)
        
        data = thisGenerator.generate(numpy.arange(0, self._numberSamples))
        
        result = thisMask.evaluate((numpy.arange(0, len(data)), data))
        
        self.assertTrue(result, 'Exponential mask failed')
        

if __name__ == "__main__":
    unittest.main()
    