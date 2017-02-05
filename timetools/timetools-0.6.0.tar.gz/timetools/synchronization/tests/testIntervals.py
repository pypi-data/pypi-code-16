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

import timetools.synchronization.intervals as si


class TestIntervals (unittest.TestCase):


    def testCalculateLogIntervalScale1 (self):
        minValue = 10
        maxValue = 120
        numberPoints = 11
        
        result = si.generateLogIntervalScale(minValue, maxValue, numberPoints)
        
        self.assertTrue(len(result) == numberPoints, 'Result does not have correct length')
        
        minValueTolerance = spt.ToleranceValue(minValue, 0.1, spt.ToleranceUnit['percent'])
        maxValueTolerance = spt.ToleranceValue(maxValue, 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue((minValueTolerance.isWithinTolerance(result[0]) and maxValueTolerance.isWithinTolerance(result[-1])), 'Incorrect endpoints')
        
        # A logarithmic sequence will be evenly spaced in the logarithmic domain
        logIntervals = numpy.diff(numpy.log10(result))
        
        intervalTolerance = spt.ToleranceValue(numpy.mean(logIntervals), 0.1, spt.ToleranceUnit['percent'])
        self.assertTrue(numpy.all(intervalTolerance.isWithinTolerance(logIntervals)), 'Intervals are not logarithmic')
        
        
    def testGenerateMonotonicLogScale1 (self):
        minValue = 10
        maxValue = 25
        numberPoints = 12
        expectedSequence = numpy.array([10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 23, 25])
        
        thisArray = si.generateLogIntervalScale(minValue, maxValue, numberPoints)
        thisIntegerArray = numpy.floor(thisArray)
        
        monotonicIntervals = si.generateMonotonicLogScale(thisIntegerArray)
        
        self.assertTrue(isinstance(monotonicIntervals[0], numpy.intp), '')
        self.assertTrue(len(monotonicIntervals) == len(expectedSequence), 'Incorrect length of monotonic sequence')
        self.assertTrue(numpy.all(monotonicIntervals == expectedSequence), 'Monotonicity failed')
            


if __name__ == "__main__":
    unittest.main()
    