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


class TestTolerance (unittest.TestCase):

    def testTolerancePercent1 (self):
        actualValue = 10.3
        
        expectedValue = 10
        toleranceValue = 5
        thisToleranceUnit = spt.ToleranceUnit['percent']
        testTolerance = spt.ToleranceValue(expectedValue, toleranceValue, thisToleranceUnit)
        
        result = testTolerance.isWithinTolerance(actualValue)
        
        self.assertTrue(result, 'Symmetric higher percent failed')
        

    def testTolerancePercent2 (self):
        actualValue = 9.7
        
        expectedValue = 10
        thisToleranceUnit = spt.ToleranceUnit['percent']
        
        toleranceValue1 = 5
        testTolerance1 = spt.ToleranceValue(expectedValue, toleranceValue1, thisToleranceUnit)
        
        result1 = testTolerance1.isWithinTolerance(actualValue)
        
        self.assertTrue(result1, 'Symmetric lower percent failed')
        
        toleranceValue2 = 2
        testTolerance2 = spt.ToleranceValue(expectedValue, toleranceValue2, thisToleranceUnit)
        
        result2 = testTolerance2.isWithinTolerance(actualValue)
        
        self.assertFalse(result2, 'Symmetric lower percent (false) failed')
        

    def testTolerancePercent3 (self):
        actualValue = numpy.array([9.7, 10.1])
        
        expectedValue = 10
        toleranceValue = [4, 2]
        thisToleranceUnit = spt.ToleranceUnit['percent']
        testTolerance = spt.ToleranceValue(expectedValue, toleranceValue, thisToleranceUnit)
        
        result = testTolerance.isWithinTolerance(actualValue)
        
        self.assertTrue(result, 'Symmetric min/max percent failed')

    def testTolerancePercent4 (self):
        actualValue = -10.3
        
        expectedValue = -10
        thisToleranceUnit = spt.ToleranceUnit['percent']
        
        toleranceValue1 = 5
        testTolerance1 = spt.ToleranceValue(expectedValue, toleranceValue1, thisToleranceUnit)
        
        result1 = testTolerance1.isWithinTolerance(actualValue)
        
        self.assertTrue(result1, 'Symmetric percent, negative expected value failed')
        
        toleranceValue2 = 2
        testTolerance2 = spt.ToleranceValue(expectedValue, toleranceValue2, thisToleranceUnit)
        
        result2 = testTolerance2.isWithinTolerance(actualValue)
        
        self.assertFalse(result2, 'Symmetric percent, negative expected value (false) failed')
        

    def testToleranceAbsolute1 (self):
        actualValue = numpy.array([9.7, 10.1])
        
        expectedValue = 10
        toleranceValue = 9.65
        thisToleranceUnit = spt.ToleranceUnit['absolute']
        
        with self.assertRaises(spt.ToleranceException):
            testTolerance = spt.ToleranceValue(expectedValue, toleranceValue, thisToleranceUnit)
            
            result = testTolerance.isWithinTolerance(actualValue)
        

    def testToleranceAbsolute2 (self):
        actualValue = numpy.array([9.7, 10.1])
        
        expectedValue = 10
        toleranceValue = [9.65, 10.15]
        thisToleranceUnit = spt.ToleranceUnit['absolute']
        testTolerance = spt.ToleranceValue(expectedValue, toleranceValue, thisToleranceUnit)
        
        result = testTolerance.isWithinTolerance(actualValue)
        
        self.assertTrue(result, 'Symmetric min/max absolute failed')
        

    def testToleranceRelative1 (self):
        actualValue = numpy.array([9.7, 10.2])
        
        expectedValue = 10
        thisToleranceUnit = spt.ToleranceUnit['relative']
        
        toleranceValue1 = 0.4
        testTolerance1 = spt.ToleranceValue(expectedValue, toleranceValue1, thisToleranceUnit)
        
        result1 = testTolerance1.isWithinTolerance(actualValue)
        
        self.assertTrue(result1, 'Symmetric min/max relative failed')
        
        toleranceValue2 = 0.1
        testTolerance2 = spt.ToleranceValue(expectedValue, toleranceValue2, thisToleranceUnit)
        
        result2 = testTolerance2.isWithinTolerance(actualValue)
        
        self.assertFalse(result2, 'Symmetric min/max (false) relative failed')
        

    def testToleranceRelative2 (self):
        actualValue = numpy.array([9.7, 10.1])
        
        expectedValue = 10
        toleranceValue = [0.4, 0.2]
        thisToleranceUnit = spt.ToleranceUnit['relative']
        testTolerance = spt.ToleranceValue(expectedValue, toleranceValue, thisToleranceUnit)
        
        result = testTolerance.isWithinTolerance(actualValue)
        
        self.assertTrue(result, 'Asymmetric min/max relative failed')
        

    def testToleranceRelative3 (self):
        actualValue = numpy.array([-9.7, -10.1])
        
        expectedValue = -10
        thisToleranceUnit = spt.ToleranceUnit['relative']
        
        toleranceValue1 = [0.2, 0.4]
        testTolerance1 = spt.ToleranceValue(expectedValue, toleranceValue1, thisToleranceUnit)
        
        result1 = testTolerance1.isWithinTolerance(actualValue)
        
        self.assertTrue(result1, 'Asymmetric min/max relative, negative expected value failed')
        
        toleranceValue2 = [0.4, 0.2]
        testTolerance2 = spt.ToleranceValue(expectedValue, toleranceValue2, thisToleranceUnit)
        
        result2 = testTolerance2.isWithinTolerance(actualValue)
        
        self.assertFalse(result2, 'Asymmetric min/max relative, negative expected value (false) failed')


if __name__ == "__main__":
    unittest.main()
    