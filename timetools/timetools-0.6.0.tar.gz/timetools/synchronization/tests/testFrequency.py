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

import timetools.synchronization.frequency as tsf


class TestFrequency (unittest.TestCase):

    def testConvertSkewToFfoPpb(self):
        inputSkew = numpy.array([1.003, 1.000006, 1.00000005])
        expectedFfoPpb = numpy.array([3e6, 6e3, 50])
        
        actualFfoPpb = tsf.convertSkewToFfoPpb(inputSkew)
        
        thisTolerance = spt.ToleranceValue(expectedFfoPpb, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualFfoPpb)), 'Calculated FFO not equivalent')


    def testConvertFfoPpbToSkew(self):
        inputFfoPpb = numpy.array([3e6, 6e3, 50])
        expectedSkew = numpy.array([1.003, 1.000006, 1.00000005])
        
        actualSkew = tsf.convertFfoPpbToSkew(inputFfoPpb)
        
        thisTolerance = spt.ToleranceValue((expectedSkew - 1), 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualSkew - 1)), 'Calculated skew not equivalent')


    def testConvertFfoPpbToOffsetHz1(self):
        referenceFrequencyHz = 10e6
        inputFfoPpb = numpy.array([300, 6000, 50])
        expectedOffsetHz = numpy.array([3, 60, 0.5])
        
        actualOffsetHz = tsf.convertFfoPpbToOffsetHz(inputFfoPpb, referenceFrequencyHz)
        
        thisTolerance = spt.ToleranceValue(expectedOffsetHz, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualOffsetHz)), 'Frequency offset calculated from ppb not equivalent')


    def testConvertFfoPpbToOffsetHz2(self):
        referenceFrequencyHz = numpy.array([10e6, 1.5e9, 200e6])
        inputOffsetPpb = numpy.array([300, 6000, 50])
        expectedOffsetHz = numpy.array([3, 9000, 10])
        
        actualOffsetHz = tsf.convertFfoPpbToOffsetHz(inputOffsetPpb, referenceFrequencyHz)
        
        thisTolerance = spt.ToleranceValue(expectedOffsetHz, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualOffsetHz)), 'Array Frequency offset calculated from ppb not equivalent')


    def testConvertSkewToOffsetHz1(self):
        referenceFrequencyHz = 10e6
        inputFfoPpb = numpy.array([300, 6000, 50])
        inputSkew = tsf.convertFfoPpbToSkew(inputFfoPpb)
        expectedOffsetHz = numpy.array([3, 60, 0.5])
        
        actualOffsetHz = tsf.convertSkewToOffsetHz(inputSkew, referenceFrequencyHz)
        
        thisTolerance = spt.ToleranceValue(expectedOffsetHz, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualOffsetHz)), 'Frequency offset calculated from skew not equivalent')


    def testConvertSkewToOffsetHz2(self):
        referenceFrequencyHz = numpy.array([10e6, 1.5e9, 200e6])
        inputFfoPpb = numpy.array([300, 6000, 50])
        inputSkew = tsf.convertFfoPpbToSkew(inputFfoPpb)
        expectedOffsetHz = numpy.array([3, 9000, 10])
        
        actualOffsetHz = tsf.convertSkewToOffsetHz(inputSkew, referenceFrequencyHz)
        
        thisTolerance = spt.ToleranceValue(expectedOffsetHz, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualOffsetHz)), 'Array Frequency offset calculated from skew not equivalent')


    def testConvertFfoPpbToHz1(self):
        referenceFrequencyHz = 10e6
        inputFfoPpb = numpy.array([300, 6000, 50])
        expectedFrequencyHz = numpy.array([3, 60, 0.5]) + referenceFrequencyHz
        
        actualFrequencyHz = tsf.convertFfoPpbToHz(inputFfoPpb, referenceFrequencyHz)
        
        thisTolerance = spt.ToleranceValue(expectedFrequencyHz, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualFrequencyHz)), 'Frequency calculated from ppb not equivalent')


    def testConvertFfoPpbToHz2(self):
        referenceFrequencyHz = numpy.array([10e6, 1.5e9, 200e6])
        inputFfoPpb = numpy.array([300, 6000, 50])
        expectedFrequencyHz = numpy.array([3, 9000, 10]) + referenceFrequencyHz
        
        actualFrequencyHz = tsf.convertFfoPpbToHz(inputFfoPpb, referenceFrequencyHz)
        
        thisTolerance = spt.ToleranceValue(expectedFrequencyHz, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualFrequencyHz)), 'Array Frequency calculated from ppb not equivalent')


    def testConvertSkewToHz1(self):
        referenceFrequencyHz = 10e6
        inputFfoPpb = numpy.array([300, 6000, 50])
        inputSkew = tsf.convertFfoPpbToSkew(inputFfoPpb)
        expectedFrequencyHz = numpy.array([3, 60, 0.5]) + referenceFrequencyHz
        
        actualFrequencyHz = tsf.convertSkewToHz(inputSkew, referenceFrequencyHz)
        
        thisTolerance = spt.ToleranceValue(expectedFrequencyHz - referenceFrequencyHz, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualFrequencyHz - referenceFrequencyHz)), 'Frequency calculated from skew not equivalent')


    def testConvertSkewToHz2(self):
        referenceFrequencyHz = numpy.array([10e6, 1.5e9, 200e6])
        inputFfoPpb = numpy.array([300, 6000, 50])
        inputSkew = tsf.convertFfoPpbToSkew(inputFfoPpb)
        expectedFrequencyHz = numpy.array([3, 9000, 10]) + referenceFrequencyHz
        
        actualFrequencyHz = tsf.convertSkewToHz(inputSkew, referenceFrequencyHz)
        
        thisTolerance = spt.ToleranceValue(expectedFrequencyHz - referenceFrequencyHz, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(thisTolerance.isWithinTolerance(actualFrequencyHz - referenceFrequencyHz)), 'Array Frequency calculated from skew not equivalent')


if __name__ == "__main__":
    unittest.main()
    