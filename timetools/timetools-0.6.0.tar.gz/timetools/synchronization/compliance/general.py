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

import timetools.synchronization.compliance.analysis as complianceAnalysis


def createSimpleThresholdMask (threshold, start=0.0, stop=None, lowerThreshold=None):
    '''
    Create a static threshold mask over a specified interval. 
    
    If stop is unspecified then the interval is assumed to be closed to infinity.
    The start of the interval is assumed to be zero unless specified otherwise.
    If lowerThreshold is unspecified then the mask is assumed to be less than 
    threshold.
    If lowerThresold is specified then the mask is assumed to be closed within 
    threshold and lowerThreshold.
    '''
    thisMask = []
    if stop == None:
        if lowerThreshold == None:
            thisMask = complianceAnalysis.Mask([( [start], [threshold] )])
        else:
            thisMask = complianceAnalysis.Mask([( [start], [threshold], [lowerThreshold] )])
            
    else:
        if lowerThreshold == None:
            thisMask = complianceAnalysis.Mask([( [start, stop], [threshold] )])
        else:
            thisMask = complianceAnalysis.Mask([( [start, stop], [threshold], [lowerThreshold] )])
        
    return thisMask
