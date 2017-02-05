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

import timetools.signalProcessing.sampling as sps


class TestSampling(unittest.TestCase):
    def testUpsample1 (self):
        upsampleRatio = 2
        x = numpy.array([1, 3, 6])
        expectedNewX = numpy.array([1, 1, 3, 3, 6, 6])
        
        actualNewX = sps.upsample(x, upsampleRatio)
        
        self.assertTrue(numpy.all(expectedNewX == actualNewX), 'Failed to upsample')
        
        
    def testUpsample2 (self):
        upsampleRatio = 4
        x = numpy.array([3])
        expectedNewX = numpy.array([3, 3, 3, 3])
        
        actualNewX = sps.upsample(x, upsampleRatio)
        
        self.assertTrue(numpy.all(expectedNewX == actualNewX), 'Failed to upsample from length 1 array')
        
        
    def testUpsample3 (self):
        # Specify a floating point upsamplingRatio
        upsampleRatio = 4.0
        x = numpy.array([3])
        expectedNewX = numpy.array([3, 3, 3, 3])
        
        actualNewX = sps.upsample(x, upsampleRatio)
        
        self.assertTrue(numpy.all(expectedNewX == actualNewX), 'Failed to upsample from length 1 array')


if __name__ == "__main__":
    unittest.main()
    