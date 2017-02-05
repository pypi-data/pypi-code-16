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

import timetools.synchronization.analysis.fastMtie as tsam
import timetools.synchronization.compliance.ituTG8263.wanderGeneration as tscg8263wg


def analyzeItuTG8263Mask (localTimeSeconds, referenceTimeSeconds, samplingIntervalSeconds, desiredNumberObservations):
    mtieSeconds, observationIntervalsSeconds = tsam.calculateMtie(localTimeSeconds, 
                                                                  referenceTimeSeconds, 
                                                                  samplingIntervalSeconds, 
                                                                  desiredNumberObservations)
    
    mtieNanoseconds = mtieSeconds / 1e-9
    
    analysisResult = tscg8263wg.constantTemperatureMtieNs.evaluate( (observationIntervalsSeconds, mtieNanoseconds) )
    
    return analysisResult, tscg8263wg.constantTemperatureMtieNs, (observationIntervalsSeconds, mtieNanoseconds)
