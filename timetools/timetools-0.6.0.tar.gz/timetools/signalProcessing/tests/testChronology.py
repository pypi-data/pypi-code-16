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

import timetools.signalProcessing.chronology.chronology as spcc


class TestChronology(unittest.TestCase):
    def setUp(self):
        self._numberSamples = 100
        timebase = numpy.arange(0, self._numberSamples)
        data = numpy.random.normal(0, 1, self._numberSamples)
        
        self._testData = spcc.Chronology(timebase, data)
        
        unittest.TestCase.setUp(self)
        

    def testLen (self):
        expectedNumberSamples = self._numberSamples
        
        actualNumberSamples = len(self._testData)
        
        self.assertTrue(expectedNumberSamples == actualNumberSamples, "Number samples not matched")


if __name__ == "__main__":
    unittest.main()
    