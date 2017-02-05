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

import timetools.signalProcessing.tolerance as tst

import timetools.synchronization.analysis.ituTG810 as tsag810


class TestAdev(unittest.TestCase):

    def testAdev(self):
        samplingInterval = 1 / 16
        expectedAdev = numpy.array([3.040360199, 4.718071667, 5.432764527, 2.087627178])
        timeError = numpy.array([-.344788, .92560862, .54803764, .34023544, .80743815, -.1344168, 1.75104404, -.29410305, -.39444904, .11585753])
        desiredNumberObservations = 4
        
        referenceTime = numpy.arange(0, len(timeError))
        localTime = referenceTime + timeError
        
        actualAdev, observationIntervals = tsag810.calculateAdev(localTime, referenceTime, samplingInterval, desiredNumberObservations)
        
        self.assertTrue(len(actualAdev) == len(observationIntervals), 'Array lengths not equal')
        self.assertTrue(len(actualAdev) == desiredNumberObservations, 'Unexpected array length')
        
        thisTolerance = tst.ToleranceValue(expectedAdev, 0.01, tst.ToleranceUnit['percent'])
        self.assertTrue(thisTolerance.isWithinTolerance(actualAdev), 'Unexpected ADEV result')


if __name__ == "__main__":
    unittest.main()
    