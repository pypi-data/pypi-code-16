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

import timetools.synchronization.analysis.ituTG810 as sag810


class TestG810 (unittest.TestCase):
    
    def testTimeError (self):
        localTime = numpy.array([4, 5, 6])
        referenceTime = numpy.array([1, 2, 3])
        
        expectedTimeError = localTime - referenceTime
        
        actualTimeError = sag810.calculateTimeError(localTime, referenceTime)
        
        self.assertTrue((len(expectedTimeError) == len(actualTimeError)), 'Time errors mismatched lengths')
        self.assertTrue(numpy.all(expectedTimeError == actualTimeError), 'Actual time error != expected')


if __name__ == "__main__":
    unittest.main()
    