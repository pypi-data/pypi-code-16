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

import timetools.signalProcessing.tolerance as spt
import timetools.synchronization.time as st

import timetools.pdv.generator.ituTG8263.flicker as pgfG8263


class TestItuTG8263(unittest.TestCase):
    
    def testGenerator (self):
        timeStepSeconds = 1 / 16
        numberSamples = math.floor((3 * 240) / timeStepSeconds)
        
        referenceTimeGenerator = st.referenceGenerator(timeStepSeconds)
        
        thisParameters = pgfG8263.Parameters()
        thisGenerator = pgfG8263.Generator(thisParameters)
            
        referenceTimeSeconds = referenceTimeGenerator.generate(numberSamples)
    
        pdvSeconds = thisGenerator.generate(referenceTimeSeconds)
        
        # A weak test, but it can help catch some simple errors
        self.assertTrue(numpy.all(pdvSeconds != 0), 'As defined, zero values cannot occur in G.8263 flicker PDV')
        self.assertTrue(numpy.all(pdvSeconds >= 57.32e-6), 'Minima below absolute floor')
        self.assertTrue(numpy.all(pdvSeconds < 1), 'PDV badly scaled')
    
    
    def testComputeFlickerCoefficients (self):
        r = 2.5
        m = 8
        expectedPhi = numpy.array([ 0.3940922442, 0.6813269464, 0.8570358810, 0.9401069843, 0.9755948055, 0.9901652942, 0.9960544364, 0.9984199016])
        expectedTheta = numpy.array([ 0.13, 0.3940922442, 0.6813269464, 0.8570358810, 0.9401069842, 0.9755948055, 0.9901652942, 0.9960544364])
        
        actualPhi, actualTheta = pgfG8263.computeFlickerCoefficients(r, m)
        
        self.assertTrue(len(actualPhi) == len(expectedPhi), 'phi length failed')
        self.assertTrue(len(actualTheta) == len(expectedTheta), 'theta length failed')
        self.assertTrue(len(actualPhi) == m, 'M length failed')
        
        # Assume that erroneous implementation will result in large errors in phi, theta
        phiTolerance = spt.ToleranceValue(expectedPhi, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(phiTolerance.isWithinTolerance(actualPhi), 'phi unexpected value')
        
        thetaTolerance = spt.ToleranceValue(expectedTheta, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(thetaTolerance.isWithinTolerance(actualTheta), 'phi unexpected value')
        
    
    def testComputeLoadFlickerNoisePercent (self):
        r = 2.5
        m = 8
        
        expectedLoadVariationPercent = numpy.array([96.56252846, 86.93099049, 1.15899485, 28.04391115, 61.43113684, 0.0, 40.41425193, 27.06329919, 74.07535659, 100.0 ])
        
        phi, theta = pgfG8263.computeFlickerCoefficients(r, m)
        
        inputNoise = numpy.array([0.32147493, -0.12112488, -1.07884806, 0.33620519, 0.41851156, -0.77324752, 0.5063252,  -0.16901545,  0.58983606,  0.32557786])

        actualLoadVariationPercent = pgfG8263.computeLoadFlickerNoisePercent(inputNoise, phi, theta)

        # Assume that any implementation errors will result in large scale changes to the result
        loadTolerance = spt.ToleranceValue(expectedLoadVariationPercent, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(loadTolerance.isWithinTolerance(actualLoadVariationPercent), 'Flicker load variation not equivalent')
        
    
    def testGammaCoefficients1 (self):
        # Rec. ITU-T G.8263/Y.1363 (2012)/Amd.2 (05/2014), pp10
        networkLoadPercent = numpy.array([60])
        
        expectedCoefficients = numpy.array([[8.0255194029732E+00], [3.8429770506754E-06], [2.0554033188099E-06]])
        
        coefficientsTuple = pgfG8263.computeGammaCoefficients(networkLoadPercent)

        actualCoefficients = numpy.array(coefficientsTuple)
        
        value = spt.ToleranceValue(expectedCoefficients, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(value.isWithinTolerance(actualCoefficients)), 'G.8263 60% load example Gamma coefficients failed')
    
    
    def testGammaCoefficients2 (self):
        # Rec. ITU-T G.8263/Y.1363 (2012)/Amd.2 (05/2014), pp10
        networkLoadPercent = numpy.array([99.2])
        
        expectedCoefficients = numpy.array([[2.0132036140218E+01], [2.96693980102245E-06], [5.59439990063761E-05]])

        coefficientsTuple = pgfG8263.computeGammaCoefficients(networkLoadPercent)

        actualCoefficients = numpy.array(coefficientsTuple)
        
        value = spt.ToleranceValue(expectedCoefficients, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(value.isWithinTolerance(actualCoefficients)), 'G.8263 99.2% load example Gamma coefficients failed')


if __name__ == "__main__":
    unittest.main()
    