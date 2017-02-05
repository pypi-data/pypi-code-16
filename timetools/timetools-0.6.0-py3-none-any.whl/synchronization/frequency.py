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


def convertSkewToFfoPpb (skew):
    '''
    Convert frequency skew to Fraction Frequency Offset (FFO) in ppb.
    '''
    return((skew - 1) / 1e-9)


def convertFfoPpbToSkew (ffoPpb):
    '''
    Convert frequency skew to Fraction Frequency Offset (FFO) in ppb.
    '''
    return((ffoPpb * 1e-9) + 1)


def convertFfoPpbToOffsetHz (ffoPpb, referenceFrequencyHz):
    '''
    Convert Fractional Frequency Offset (FFO) in ppb to FFO in Hz.
    
    The reference frequency in Hz also needs to be specified.
    '''

    return(ffoPpb * referenceFrequencyHz * 1e-9)


def convertSkewToOffsetHz (skew, referenceFrequencyHz):
    '''
    Convert Fractional Frequency Offset (FFO) in ppb to FFO in Hz.
    
    The reference frequency in Hz also needs to be specified.
    '''

    return((skew * referenceFrequencyHz) - referenceFrequencyHz)


def convertFfoPpbToHz (ffoPpb, referenceFrequencyHz):
    '''
    Convert Fractional Frequency Offset (FFO) in ppb to absolute frequency in Hz.
    
    The reference frequency in Hz also needs to be specified.
    '''

    return((ffoPpb * referenceFrequencyHz * 1e-9) + referenceFrequencyHz)


def convertSkewToHz (skew, referenceFrequencyHz):
    '''
    Convert Fractional Frequency Offset (FFO) in ppb to absolute frequency in Hz.
    
    The reference frequency in Hz also needs to be specified.
    '''

    return(skew * referenceFrequencyHz)
