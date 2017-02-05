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
import timetools.signalProcessing.chronology.sampling as spcs

class TestChronologySampling (unittest.TestCase):

    def testDecimate1(self):
        timebase = numpy.arange(0, 10)
        signal = numpy.arange(0, 10) + 5
        
        inputChronology = spcc.Chronology(timebase, signal)
        
        expectedTimebase = timebase[0 : 2 : len(timebase)]
        expectedSignal = signal[0 : 2 : len(signal)]
        
        outputChronology = spcs.decimate(inputChronology, 2)
        
        self.assertTrue(numpy.all(expectedTimebase == outputChronology.timebase), 'Actual timebase is not expected after decimation')
        self.assertTrue(numpy.all(expectedSignal == outputChronology.signal), 'Actual signal is not expected after decimation')


if __name__ == "__main__":
    unittest.main()
    