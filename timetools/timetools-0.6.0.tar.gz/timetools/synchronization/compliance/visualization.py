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

import matplotlib.pyplot as mpp


class plot:
    
    def __init__ (self):
        self._masks = []
        self._signals = []
        
        
    def addMask (self, thisMask, *args, **kwargs):
        self._masks.append( (thisMask, kwargs) )
        
        
    def addSignal (self, thisSignal, *args, **kwargs):
        self._signals.append( (thisSignal, kwargs) )
        
        
    def go (self):
        figureHandle = mpp.figure()
        
        for thisElement in self._signals:
            thisSignal = thisElement[0]
            signalKwargs = thisElement[1]
            
            signalBaseline = thisSignal[0]
            signalValues = thisSignal[1]
        
            mpp.plot(signalBaseline, signalValues, **signalKwargs)
            
        # Add the masks last so that they are on top
        for thisElement in self._masks:
            thisMask = thisElement[0]
            maskKwargs = thisElement[1]
            
            thisMask.addToPlot(figureHandle.number, **maskKwargs)
            
        return figureHandle
        