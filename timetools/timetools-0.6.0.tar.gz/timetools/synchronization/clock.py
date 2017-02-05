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


def calculateLocalTimeFromFfo(
        referenceTimeSeconds,
        loFfoPpb,
        initialFfoPpb = 0,
        initialReferenceTimeSeconds = 0,
        initialLocalTimeSeconds = 0 ):
    assert ( loFfoPpb.shape == referenceTimeSeconds.shape )

    # Make sure that the FFO from a previous iteration is accurately accounted for.
    initialFfoArray = numpy.array( [ initialFfoPpb ] )
    if loFfoPpb != []:
        instantaneousFfoPpb = numpy.concatenate( ( initialFfoArray, loFfoPpb[ : ( len( loFfoPpb ) - 1 ) ] ) )
    else:
        instantaneousFfoPpb = initialFfoArray

    timeDelta = numpy.diff( numpy.concatenate( ( numpy.array( [ initialReferenceTimeSeconds ] ), referenceTimeSeconds ) ) )

    assert ( instantaneousFfoPpb.shape == timeDelta.shape )

    timeChange = ( timeDelta * instantaneousFfoPpb * 1e-9 ) + timeDelta
    localTimeSeconds = numpy.array( [ initialLocalTimeSeconds ] ) + numpy.cumsum( timeChange )

    assert ( localTimeSeconds.shape == referenceTimeSeconds.shape )

    return localTimeSeconds


class ClockModel:
    '''
        A simple clock model with initial static offset and optional Gaussian frequency
        jitter. The initial time offset is assumed to be zero.

        The frequency offset and resulting time offset are returned by
        calculateOffset. calculateOffset is iterative so that subsequent calls to
        calculateOffset calculate the offset relative to the last call.
    '''
    
    def __init__( self, oscillatorModel,
                  initialTimeOffsetSeconds = 0,
                  initialReferenceTimeSeconds = 0,
                  initialReferenceTemperatureKelvin = 0 ):
        # Support iterative use of the model by retaining relevant data from the previous iteration.
        self.lastReferenceTimeSeconds = initialReferenceTimeSeconds
        self.lastReferenceTemperatureKelvin = initialReferenceTemperatureKelvin
        self.lastLocalTimeOffsetSeconds = initialTimeOffsetSeconds
        self.lastInstantaneousFfoPpb = oscillatorModel.initialFfoPpb

        self.oscillatorModel = oscillatorModel
        

    def generate( self, referenceTimeSeconds, referenceTemperatureKelvin = None ):
        loFfoPpb = \
            self.oscillatorModel.generate(
                referenceTimeSeconds,
                referenceTemperatureKelvin )

        # If there is any time delta between self._lastReferenceTimeSeconds and referenceTimeSeconds[0]
        # then this must be accounted for in the skew and subsequent time integration calculation.
        localTimeSeconds = \
            calculateLocalTimeFromFfo(
                referenceTimeSeconds,
                loFfoPpb,
                self.lastInstantaneousFfoPpb,
                self.lastReferenceTimeSeconds,
                self.lastLocalTimeOffsetSeconds )
        
        self.lastLocalTimeOffsetSeconds = localTimeSeconds[-1 ]
        self.lastInstantaneousFfoPpb = loFfoPpb[-1 ]
        # Make this a numpy array even though it is only a single scalar so that numpy concatenation works for
        # timeDelta calculation.
        self.lastReferenceTimeSeconds = referenceTimeSeconds[-1 ]
        if referenceTemperatureKelvin is not None:
            self.lastReferenceTemperatureKelvin = referenceTemperatureKelvin[-1 ]
        
        return localTimeSeconds, loFfoPpb
    