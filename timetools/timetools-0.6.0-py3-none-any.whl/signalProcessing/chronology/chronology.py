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

import timetools.signalProcessing.exceptions as spe


class Chronology:
    def __init__ (self, timebase = [], signal = []):
        if len(timebase) != len(signal):
            raise spe.SignalProcessingException('Chronology timebase and signals lengths must be equal')
        
        # timebase must be monotonic
        delta = numpy.diff(timebase)
        if not numpy.all(delta >= 0):
            raise spe.SignalProcessingException('Chronology timebase is not monotonically increasing')
        
        self.timebase = timebase
        self.signal = signal
        
        
    def __len__ (self):
        assert(len(self.timebase) == len(self.signal))
        
        return len(self.timebase)
    
    
    def __getitem__ (self):
        pass
    
    
    def __setitem__ (self):
        pass
        
        
    def __lt__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] < thisChronology.signal
        
        return dataResult
        
        
    def __le__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] <= thisChronology.signal
        
        return dataResult
    
    
    def __gt__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] > thisChronology.signal
        
        return dataResult
    
    
    def __ge__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] >= thisChronology.signal
        
        return dataResult
    
    
    def __eq__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] == thisChronology.signal
        
        return dataResult
    
    
    def __ne__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] != thisChronology.signal
        
        return dataResult
    
    
    def __add__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] + thisChronology.signal
        
        return dataResult
    
    
    def __sub__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] - thisChronology.signal
        
        return dataResult
    
    
    def __mul__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] * thisChronology.signal
        
        return dataResult
    
    
    def __floordiv__(self, other):
        return NotImplemented
    
    
    def __mod__(self, other):
        return NotImplemented
    

    def __divmod__(self, other):
        return NotImplemented
    
    
    def __pow__(self, other):
        return NotImplemented
    
    
    def __lshift__(self, other):
        return NotImplemented
    
    
    def __rshift__(self, other):
        return NotImplemented
    
    
    def __and__(self, other):
        return NotImplemented
    
    
    def __xor__(self, other):
        return NotImplemented
    
    
    def __or__(self, other):
        return NotImplemented
    
    
    def __div__ (self, thisChronology):
        logicalIndices = self._getLogicalIndices(thisChronology.timebase)
        dataResult = self.signal[logicalIndices] / thisChronology.signal
        
        return dataResult
    
    
    def _getLogicalIndices (self, timebase):
        logicalIndices = self.timebase == timebase
        
        return logicalIndices
    