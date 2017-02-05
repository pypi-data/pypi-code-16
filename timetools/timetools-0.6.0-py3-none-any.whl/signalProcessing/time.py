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
import time


def printTime (elapsedTimeSeconds):
    timeText = ''
    if elapsedTimeSeconds >= 3600:
        hrs = math.floor(elapsedTimeSeconds / 3600)
        timeText += (repr(hrs) + ' hrs, ')
        
        remainder = elapsedTimeSeconds - (hrs * 3600)
        
        timeText += printTime(remainder)
    elif elapsedTimeSeconds >= 60:
        mins = math.floor(elapsedTimeSeconds / 60)
        timeText += (repr(mins) + ' min, ')
        
        remainder = elapsedTimeSeconds - (mins * 60)
        
        timeText += printTime(remainder)
    else:
        timeText = repr(elapsedTimeSeconds) + ' s'
        
    return timeText


class StopWatch:
    
    def __init__( self ):
        self._timers = []
        self._lastTime = self._startTime
        
        self._timers.append( time.time() )
        
        
    def showElapsed( self, thisMessage ):
        currentTime = time.time()
        self.timers.append( currentTime )

        elapsedTime = currentTime - self._lastTime
        
        print( thisMessage + printTime( elapsedTime ) )
        
        self._lastTime = currentTime
        
        
    def showTotal( self, thisMessage ):
        currentTime = time.time()
        elapsedTime = currentTime - self._timers[0]
        
        print( thisMessage + printTime( elapsedTime ) )
        
        
    def recordTimer( self ):
        self.timers.append( time.time() )
        
        
    def reportTimers( self ):
        return self._timers
    