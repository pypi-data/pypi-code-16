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


class TestMdev(unittest.TestCase):

    def testMdev(self):
        samplingInterval = 1 / 16
        expectedMdev = numpy.array([18.26359894, 9.679294116, 6.050149415, 3.784818216])
        expectedObservationIntervals = numpy.array([0.0625, .125, .1875, .25])
        timeError = numpy.array([-0.15972281, -0.29278757, -0.8524681 ,  1.29062037,  1.1266783 ,
                                 0.55233637,  1.13049531,  0.64285149, -0.00997373, -1.51331045,
                                 0.33250817,  1.08550563,  0.00975715, -0.21406682,  0.65904871])
        # Compensating for the logarithmic observation interval scale used internally, over specify
        # the desired number and then reduce after MDEV calculation.
        desiredNumberObservations = 5
        
        referenceTime = numpy.arange(0, len(timeError))
        localTime = referenceTime + timeError
        
        calculatedMdev, observationIntervals = tsag810.calculateMdev(localTime, referenceTime, samplingInterval, desiredNumberObservations)
        
        actualMdev = calculatedMdev[0:-1]
        actualObservationIntervals = observationIntervals[0:-1]
        
        self.assertTrue(len(actualMdev) == len(actualObservationIntervals), 'Array lengths not equal')
        self.assertTrue(len(actualMdev) == len(expectedMdev), 'Unexpected array length')
        
        intervalTolerance = tst.ToleranceValue(expectedObservationIntervals, 0.01, tst.ToleranceUnit['percent'])
        self.assertTrue(intervalTolerance.isWithinTolerance(actualObservationIntervals), 'Unexpected intervals result')
        
        mdevTolerance = tst.ToleranceValue(expectedMdev, 0.01, tst.ToleranceUnit['percent'])
        self.assertTrue(mdevTolerance.isWithinTolerance(actualMdev), 'Unexpected MDEV result')


if __name__ == "__main__":
    unittest.main()
    