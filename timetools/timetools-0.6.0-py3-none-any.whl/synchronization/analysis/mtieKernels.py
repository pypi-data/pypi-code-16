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


def _calculatePeakToPeakAmplitude( signal ):
    maxError = numpy.max( signal )
    minError = numpy.min( signal )
    
    peakToPeakAmplitude = maxError - minError
    
    return peakToPeakAmplitude


def slidingWindow( timeError, thisInterval ):
    thisMtie = 0
    for m in numpy.arange( 0, ( timeError.size - thisInterval ), 1 ):
        thisWindow = timeError[ m : ( m + thisInterval + 1 ) : 1 ]
        peakToPeakError = _calculatePeakToPeakAmplitude( thisWindow )
        
        if peakToPeakError > thisMtie:
            thisMtie = peakToPeakError
            
    return thisMtie


def smartWindow( timeError, thisInterval ):
    
    def findMaximumPosition( thisWindow, m ):
        maxWindowPosition = numpy.argmax( thisWindow )
        
        maxSignalPosition = maxWindowPosition + m
        
        return maxSignalPosition
    
    
    def findMinimumPosition( thisWindow, m ):
        minWindowPosition = numpy.argmin( thisWindow )
        
        minSignalPosition = minWindowPosition + m
        
        return minSignalPosition
    
    numberSamples= timeError.size
    
    thisMtie = 0
    
    m = 0
    completed = False
    lastIteration = False
    while not completed:
        thisWindow = timeError[ m : ( m + thisInterval + 1 ) : 1 ]        
        peakToPeakError = _calculatePeakToPeakAmplitude( thisWindow )
        
        if peakToPeakError > thisMtie:
            thisMtie = peakToPeakError
        
        maxSignalPosition = findMaximumPosition( thisWindow, m )
        minSignalPosition = findMinimumPosition( thisWindow, m )
        
        nextWindowPosition = numpy.min( [ maxSignalPosition, minSignalPosition ] )
            
        if lastIteration:
            completed = True
        elif nextWindowPosition == m:
            nextWindowPosition = m + 1
            
        if ( nextWindowPosition + thisInterval ) >= numberSamples:
            nextWindowPosition = numberSamples - thisInterval
            lastIteration = True
            
        m = nextWindowPosition
        
    return thisMtie

