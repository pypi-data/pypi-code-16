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
    

def upsample (sequence, upsamplingRatio):
    '''
    Upsample a data sequence by some integer ratio by repeating existing data.
    
    For N samples in the original array and M oversampling ratio, the 
    upsampled data has size N * M.
    '''
    # Ensure the upsamplingRatio is an integer
    thisUpsamplingRatio = int(upsamplingRatio)
    
    newNumberSamples = len(sequence) * thisUpsamplingRatio
    
    newSequence = numpy.zeros(newNumberSamples)
    for k in range(0, thisUpsamplingRatio):
        xnew = numpy.arange(k, newNumberSamples, thisUpsamplingRatio)
        newSequence[xnew] = sequence
    
    return newSequence
