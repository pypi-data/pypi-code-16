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

import math

import timetools.signalProcessing.chronology.chronology as spcc


def decimate (inputChronology, decimationRatio):
    assert((decimationRatio / math.floor(decimationRatio)) == 1)
    
    outputTimebase = inputChronology.timebase[0 : decimationRatio : len(inputChronology.timebase)]
    outputSignal = inputChronology.signal[0 : decimationRatio : len(inputChronology.signal)]
    
    return spcc.Chronology(outputTimebase, outputSignal)
