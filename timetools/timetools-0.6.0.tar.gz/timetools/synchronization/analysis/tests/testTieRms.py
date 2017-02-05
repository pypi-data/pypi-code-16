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


class TestTieRMs(unittest.TestCase):

    def testTieRms(self):
        samplingInterval = 1 / 16
        expectedTieRms = numpy.array([.9740401936, 1.294559383, 1.396806780, 1.430599252, 1.638891621, 1.666726436, .6220454931, .8695116123, 1.353587640])
        expectedObservationIntervals = numpy.array([0.6250000000e-1, .1250000000, .1875000000, .2500000000, .3125000000, .3750000000, .4375000000, .5000000000, .5625000000])
        timeError = numpy.array([-.15972281, -.29278757, -.8524681, 1.29062037, 1.1266783, .55233637, 1.13049531, .64285149, -0.997373e-2, -1.51331045])
        desiredNumberObservations = 9
        
        referenceTime = numpy.arange(0, len(timeError))
        localTime = referenceTime + timeError
        
        actualTieRms, observationIntervals = tsag810.calculateTieRms(localTime, referenceTime, samplingInterval, desiredNumberObservations)
        
        self.assertTrue(len(actualTieRms) == len(observationIntervals), 'Array lengths not equal')
        self.assertTrue(len(actualTieRms) == desiredNumberObservations, 'Unexpected array length')
        
        intervalsTolerance = tst.ToleranceValue(expectedObservationIntervals, 0.01, tst.ToleranceUnit['percent'])
        self.assertTrue(intervalsTolerance.isWithinTolerance(observationIntervals), 'Unexpected intervals result')
        
        tieTolerance = tst.ToleranceValue(expectedTieRms, 0.01, tst.ToleranceUnit['percent'])
        self.assertTrue(tieTolerance.isWithinTolerance(actualTieRms), 'Unexpected TIE RMS result')


if __name__ == "__main__":
    unittest.main()
    