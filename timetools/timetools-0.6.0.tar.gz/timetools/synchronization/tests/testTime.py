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

import timetools.synchronization.time as st


class TestTime (unittest.TestCase):

    def testTime1(self):
        referenceTimeStepSeconds = 0.5
        numberIterationSamples = 10
        numberIterations = 2
        
        referenceTimebaseSeconds = st.referenceGenerator(referenceTimeStepSeconds)
        
        collatedTimeSeconds = numpy.array([])
        for k in range(0, numberIterations):
            iterationTimeSeconds = referenceTimebaseSeconds.generate(numberIterationSamples)
            collatedTimeSeconds = numpy.append(collatedTimeSeconds, iterationTimeSeconds)
            
        expectedTimeSeconds = numpy.arange(0, (numberIterations * numberIterationSamples)) * referenceTimeStepSeconds
        
        if not numpy.all(expectedTimeSeconds == collatedTimeSeconds):
            print(repr(expectedTimeSeconds))
            print(repr(collatedTimeSeconds))
            self.assertFalse(True, 'Expected sequence does not equal actual sequence')

    def testTime2(self):
        initialTimeOffsetSeconds = 12.5
        referenceTimeStepSeconds = 0.5
        numberIterationSamples = 10
        numberIterations = 2
        
        referenceTimebaseSeconds = st.referenceGenerator(referenceTimeStepSeconds, initialTimeOffset = initialTimeOffsetSeconds)
        
        collatedTimeSeconds = numpy.array([])
        for k in range(0, numberIterations):
            iterationTimeSeconds = referenceTimebaseSeconds.generate(numberIterationSamples)
            collatedTimeSeconds = numpy.append(collatedTimeSeconds, iterationTimeSeconds)
            
        expectedTimeSeconds = numpy.arange(0, (numberIterations * numberIterationSamples)) * referenceTimeStepSeconds + initialTimeOffsetSeconds
        
        if not numpy.all(expectedTimeSeconds == collatedTimeSeconds):
            print(repr(expectedTimeSeconds))
            print(repr(collatedTimeSeconds))
            self.assertFalse(True, 'Expected sequence does not equal actual sequence')


if __name__ == "__main__":
    unittest.main()
    