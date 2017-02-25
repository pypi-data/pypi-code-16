"""
Definition of BitRange
"""
#
# Copyright 2016 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import re

import registerMap.utility.observer as rmo

import registerMap.utility.yaml.base as ryb
import registerMap.utility.yaml.encode as rye
import registerMap.utility.yaml.parse as ryp

from registerMap.exceptions import ConfigurationError, ParseError


log = logging.getLogger( __name__ )


class BitRange( ryb.Export, ryb.Import ) :
    """
    Manage BitRange concept
    """


    def __init__( self, value = None ) :
        super( ).__init__( )

        self.sizeChangeNotifier = rmo.Observable( )

        if value is not None :
            self.__validateValue( value )
        self.__value = value


    @property
    def maxValue( self ) :
        maxValue = pow( 2, self.numberBits ) - 1

        return maxValue


    @staticmethod
    def __calculateNumberBits( value ) :
        return max( value ) - min( value ) + 1


    @property
    def numberBits( self ) :
        if self.__value is None :
            returnValue = 0
        else :
            returnValue = max( self.__value ) - min( self.__value ) + 1
        return returnValue


    @property
    def value( self ) :
        return self.__value


    @value.setter
    def value( self, value ) :
        self.__validateValue( value )
        self.__value = value
        log.debug( 'Notifying of a bit range value change' )
        self.sizeChangeNotifier.notifyObservers( )


    def __eq__( self, other ) :
        if other is None :
            isEqual = self.__value is other
        elif isinstance( other, list ) :
            isEqual = self.__value == other
        elif other.__value is None :
            isEqual = self.__value is other.__value
        else :
            isEqual = self.__value == other.__value

        return isEqual


    def __ne__( self, other ) :
        return not (self == other)


    def __validateValue( self, value ) :
        errorMessage = 'Bit range must be a list of two positive integers, ' + repr( value )
        if not isinstance( value, list ) :
            raise ConfigurationError( errorMessage )

        if any( [ not isinstance( x, int ) for x in value ] ) :
            raise ConfigurationError( errorMessage )

        if any( [ True for x in value if x < 0 ] ) :
            raise ConfigurationError( errorMessage )

        if len( value ) != 2 :
            raise ConfigurationError( errorMessage )


    def __hash__( self ) :
        # Python seems to think the BitRange class is not hashable, so explicitly defining __hash__ method and returning
        # the object id fixes that.
        return id( self )


    @classmethod
    def from_yamlData( cls, yamlData ) :
        bitRange = cls( )
        goodResult = bitRange.__decodeBitRange( yamlData )

        if not goodResult :
            raise ParseError( 'Processing bit range data failed. Check log for details. ' + repr( yamlData ) )

        return bitRange


    def __decodeBitRange( self, yamlData ) :
        def recordValue( valueData ) :
            nonlocal self

            if valueData == 'None' :
                self.__value = None
            else :
                rangeData = valueData.strip( '[' ).strip( ']' )
                tokens = re.split( r':', rangeData )
                if len( tokens ) != 2 :
                    log.error( 'Range must have only two values: ' + rangeData )

                try :
                    value = [ int( tokens[ 0 ] ), int( tokens[ 1 ] ) ]
                    self.__validateValue( value )
                    self.__value = value
                except ValueError :
                    log.error( 'Range must be integers: ' + rangeData )


        keyName = 'range'

        return ryp.stringParameter( yamlData, keyName, recordValue,
                                    optional = False )


    def to_yamlData( self ) :
        keyName = 'range'
        value = '[' + str( min( self.__value ) ) + ':' + str( max( self.__value ) ) + ']'

        return rye.parameter( keyName, value )
