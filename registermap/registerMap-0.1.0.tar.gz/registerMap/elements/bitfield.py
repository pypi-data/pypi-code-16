"""
Definition of register field.
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

import registerMap.elements.bitRange as rmbr
import registerMap.utility.observer as rmo
import registerMap.utility.yaml.base as ryb
import registerMap.utility.yaml.encode as rye
import registerMap.utility.yaml.parse as ryp

# Enable users of bitField module to easily acquire access to BitRange
from registerMap.elements.bitRange import BitRange
from registerMap.exceptions import ConfigurationError, ParseError


log = logging.getLogger( __name__ )


class BitField( ryb.Export, ryb.Import ) :
    """
    Representation of a bit field in a register.
    """


    class SizeChangeObserver( rmo.Observer ) :
        def __init__( self, owner ) :
            self.__owner = owner


        def update( self, observable, arguments ) :
            # Just cascade the size change
            self.__owner.sizeChangeNotifier.notifyObservers( )


    def __init__( self ) :
        """

        :param eventService: The event service used to notify subscribers of a change.
        """
        super( ).__init__( )

        name = 'unassigned'
        self.sizeChangeNotifier = rmo.Observable( )

        self.__sizeChangeObserver = BitField.SizeChangeObserver( self )

        bitRange = self.__createBitRange( )

        self.__data = {
            'bitRange' : bitRange,
            'description' : '',
            'name' : name,
            'public' : True,
            'resetValue' : 0,
            'summary' : ''
        }
        self.__validationMethods = {
            'bitRange' : self.__validateBitRange,
            'public' : self.__validatePublic,
            'resetValue' : self.__validateResetValue
        }


    def __createBitRange( self ) :
        bitRange = rmbr.BitRange( )

        log.debug( 'Subscribing to bit range changes, ' + repr( bitRange ) + ', for ' + repr( self ) )
        bitRange.sizeChangeNotifier.addObserver( self.__sizeChangeObserver )

        return bitRange


    def __getitem__( self, item ) :
        return self.__data[ item ]


    def __setitem__( self, key, value ) :
        try :
            self.__validationMethods[ key ]( value )
        except KeyError :
            # key is not in self.__validationMethods so just apply the user specified key without validation
            pass

        self.__data[ key ] = value
        if key == 'bitRange' :
            log.debug( 'Notifying on bit field value change' )
            self.sizeChangeNotifier.notifyObservers( )


    def __validateBitRange( self, value ) :
        maxValue = value.maxValue
        if self.__data[ 'resetValue' ] > maxValue :
            raise ConfigurationError( 'Reset value cannot exceed number of bits of field, '
                                      + repr( maxValue ) + ' specified maximum, '
                                      + repr( self.__data[ 'resetValue' ] ) + ' current reset value' )


    def __validatePublic( self, value ) :
        if not isinstance( value, bool ) :
            raise ConfigurationError( 'Public must be specified as boolean' )


    def __validateResetValue( self, value ) :
        if not isinstance( value, int ) or (value < 0) :
            raise ConfigurationError( 'Reset value must be specified as non-negative integer' )

        if self.__data[ 'bitRange' ].value is None :
            raise ConfigurationError( 'Bit range not defined' )

        maxValue = self.__data[ 'bitRange' ].maxValue
        if value > maxValue :
            raise ConfigurationError( 'Reset value cannot exceed number of bits of field, '
                                      + repr( maxValue ) + ' maximum, '
                                      + repr( value ) + ' specified' )


    @classmethod
    def from_yamlData( cls, yamlData ) :
        bitField = cls( )
        goodResult = bitField.__decodeBitField( yamlData )

        if not goodResult :
            raise ParseError( 'Processing memory space data failed. Check log for details. ' + repr( yamlData ) )

        return bitField


    def __decodeBitField( self, yamlData ) :
        def recordDescription( value ) :
            nonlocal self
            self.__data[ 'description' ] = value


        def recordName( value ) :
            nonlocal self
            self.__data[ 'name' ] = value


        def recordPublic( value ) :
            nonlocal self
            self.__data[ 'public' ] = value


        def recordResetValue( value ) :
            nonlocal self
            self.__data[ 'resetValue' ] = value


        def recordSummary( value ) :
            nonlocal self
            self.__data[ 'summary' ] = value


        def getParameters( thisData ) :
            nonlocal self
            self.__data[ 'bitRange' ] = rmbr.BitRange.from_yamlData( thisData )
            # Make sure that we subscribe to notification of bit range size changes.
            self.__data[ 'bitRange' ].sizeChangeNotifier.addObserver( self.__sizeChangeObserver )

            thisGoodResult = ryp.stringParameter( thisData, 'name', recordName )
            thisGoodResult &= ryp.booleanParameter( thisData, 'public', recordPublic )
            thisGoodResult &= ryp.integerParameter( thisData, 'resetValue', recordResetValue )
            ryp.stringParameter( thisData, 'description', recordDescription,
                                 optional = True )
            ryp.stringParameter( thisData, 'summary', recordSummary,
                                 optional = True )

            return thisGoodResult


        keyName = 'bitField'

        return ryp.complexParameter( yamlData, keyName, getParameters )


    def to_yamlData( self ) :
        parameters = [ self.__data[ 'bitRange' ].to_yamlData( ),
                       rye.parameter( 'name', self.__data[ 'name' ] ),
                       rye.parameter( 'public', self.__data[ 'public' ] ),
                       rye.parameter( 'resetValue', rye.HexInt( self.__data[ 'resetValue' ] ) ) ]

        if self.__data[ 'description' ] != '' :
            parameters.append( rye.parameter( 'description', self.__data[ 'description' ] ) )
        if self.__data[ 'summary' ] != '' :
            parameters.append( rye.parameter( 'summary', self.__data[ 'summary' ] ) )

        keyName = 'bitField'
        yamlData = { keyName : { } }

        for thisParameter in parameters :
            yamlData[ keyName ].update( thisParameter )

        return yamlData
