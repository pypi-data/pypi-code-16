"""
Definition of constraints on register map artifacts.
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
import math

import registerMap.utility.observer as rmo
import registerMap.utility.yaml.base as ryb
import registerMap.utility.yaml.encode as rye
import registerMap.utility.yaml.parse as ryp

from registerMap.exceptions import ConstraintError, ParseError


log = logging.getLogger( __name__ )

constraintNames = [
    'fixedAddress',
    'fixedSizeMemoryUnits',
    'alignmentMemoryUnits'
]


class ConstraintTable :
    """
    Express constraints to be applied to RegisterMap, Module, Register or BitField.

    fixedAddress: means that the address will never change from the specified value.
    alignmentMemoryUnits: means that the address will be aligned to the next highest multiple of the specified number
    of memory units.

    fixedSize: means that the size will never change from the specified value.
    """
    __executionOrder = [ 'fixedAddress',
                         'alignmentMemoryUnits',
                         'fixedSizeMemoryUnits' ]


    def __init__( self, memory ) :
        self.addressChangeNotifier = rmo.Observable( )
        self.sizeChangeNotifier = rmo.Observable( )

        self.__memory = memory
        self.__applicators = {
            'alignmentMemoryUnits' : self.__applyAddressAlignment,
            'fixedAddress' : self.__applyFixedAddress,
            'fixedSizeMemoryUnits' : self.__applyFixedSize
        }
        self.__constraints = dict( )
        self.__validaters = {
            'alignmentMemoryUnits' : self.__validateAlignment,
            'fixedAddress' : self.__validateFixedAddress,
            'fixedSizeMemoryUnits' : self.__validateFixedSize
        }
        self.__notifiers = {
            'alignmentMemoryUnits' : self.addressChangeNotifier.notifyObservers,
            'fixedAddress' : self.addressChangeNotifier.notifyObservers,
            'fixedSizeMemoryUnits' : self.sizeChangeNotifier.notifyObservers
        }


    def __delitem__( self, key ) :
        log.debug( 'Deleting constraint, ' + repr( key ) )
        self.__validateGetName( key )
        del self.__constraints[ key ]
        self.__notifiers[ key ]( self )


    def __getitem__( self, item ) :
        self.__validateGetName( item )
        return self.__constraints[ item ]


    def __len__( self ) :
        return len( self.__constraints )


    def __setitem__( self, key, value ) :
        log.debug( 'Setting constraint value, ' + repr( key ) + ', ' + repr( value ) )
        self.__validateSetName( key, value )
        self.__constraints[ key ] = value
        self.__notifiers[ key ]( key )


    def __validateGetName( self, name ) :
        self.__validateName( name )

        if name not in self.__constraints.keys( ) :
            raise ConstraintError( 'Constraint not applied, ' + repr( name ) )


    def __validateSetName( self, name, value ) :
        self.__validateName( name )
        self.__validaters[ name ]( value )


    @staticmethod
    def __validateName( name ) :
        if name not in constraintNames :
            raise ConstraintError( 'Not a valid constraint, ' + repr( name ) )


    def applyAddressConstraints( self, addressValue ) :
        addressConstraints = [ 'fixedAddress', 'alignmentMemoryUnits' ]
        newAddress = addressValue
        for constraint in addressConstraints :
            try :
                newAddress = self.__applicators[ constraint ]( addressValue )
                addressValue = newAddress
            except KeyError as e :
                # If the constraint doesn't exist, then it simply doesn't get applied.
                pass

        return newAddress


    def applySizeConstraints( self, sizeValue ) :
        sizeConstraints = [ 'fixedSizeMemoryUnits' ]
        newSize = sizeValue
        for constraint in sizeConstraints :
            try :
                newSize = self.__applicators[ constraint ]( sizeValue )
                sizeValue = newSize
            except KeyError as e :
                # If the constraint doesn't exist, then it simply doesn't get applied.
                pass

        return newSize


    def __validateFixedAddress( self, address ) :
        if 'alignmentMemoryUnits' in self.__constraints.keys( ) :
            alignedValue = calculateAddressAlignment( address, self.__constraints[ 'alignmentMemoryUnits' ] )
            if address != alignedValue :
                raise ConstraintError( 'Fixed address conflicts with existing, fixedValue '
                                       + repr( address )
                                       + ' aligns to '
                                       + repr( alignedValue ) )

        if self.__memory.pageSize is not None :
            if self.__memory.isPageRegister( address ) :
                raise ConstraintError( 'Cannot constrain address to page register' )

        validatePositive( address, 'Fixed address' )


    def __validateFixedSize( self, value ) :
        validatePositiveNonZero( value, 'Fixed size' )


    def __validateAlignment( self, alignmentValue ) :
        if (alignmentValue is not None) and ('fixedAddress' in self.__constraints.keys( )) :
            address = self.__constraints[ 'fixedAddress' ]
            alignedValue = calculateAddressAlignment( address, alignmentValue )
            if address != alignedValue :
                raise ConstraintError( 'Alignment conflicts with existing fixed address, fixedValue '
                                       + repr( address )
                                       + ' aligns to '
                                       + repr( alignedValue ) )

        validatePositiveNonZero( alignmentValue, 'Alignment' )


    def __applyAddressAlignment( self, currentAddress ) :
        newAddress = None
        if currentAddress is not None :
            alignmentValue = self.__constraints[ 'alignmentMemoryUnits' ]
            validatePositiveNonZero( alignmentValue, 'Alignment' )

            newAddress = calculateAddressAlignment( currentAddress, alignmentValue )

        return newAddress


    def __applyFixedAddress( self, currentAddress ) :
        fixedAddress = self.__constraints[ 'fixedAddress' ]
        validatePositive( fixedAddress, 'Fixed address' )

        if (currentAddress is not None) and (currentAddress > fixedAddress) :
            raise ConstraintError( 'Fixed address exceeded, '
                                   + hex( currentAddress ) + ' (current), '
                                   + hex( fixedAddress ) + ' (constraint)' )

        return fixedAddress


    def __applyFixedSize( self, currentSize ) :
        fixedSize = self.__constraints[ 'fixedSizeMemoryUnits' ]
        validatePositiveNonZero( fixedSize, 'Fixed size' )

        if currentSize > fixedSize :
            raise ConstraintError( 'Fixed size exceeded, '
                                   + repr( currentSize ) + ' (current), '
                                   + repr( fixedSize ) + ' (constraint)' )

        return fixedSize


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace,
                       optional = False ) :
        thisConstraints = cls( memorySpace )
        goodResult = thisConstraints.__decodeConstraintTable( yamlData,
                                                              optional = optional )

        if (not goodResult) and (not optional) :
            raise ParseError( 'Processing constraint data failed. Check log for details. ' + repr( yamlData ) )

        return thisConstraints


    def __decodeConstraintTable( self, yamlData,
                                 optional = False ) :
        def recordConstraint( name, value ) :
            nonlocal self

            self[ name ] = value


        def getParameters( thisData ) :
            nonlocal self

            # All constraints are optional
            for constraint in constraintNames :
                ryp.integerParameter( thisData, constraint, recordConstraint,
                                      optional = True,
                                      useName = True )

            return True


        keyName = 'constraints'

        return ryp.complexParameter( yamlData, keyName, getParameters,
                                     optional = optional )


    def to_yamlData( self ) :
        parameters = list( )

        for constraintName, value in self.__constraints.items( ) :
            parameters.append( rye.parameter( constraintName, value ) )

        keyName = 'constraints'
        yamlData = { keyName : { } }

        for thisParameter in parameters :
            yamlData[ keyName ].update( thisParameter )

        return yamlData


def calculateAddressAlignment( currentAddress, alignmentValue ) :
    newAddress = math.ceil( float( currentAddress ) / alignmentValue ) * alignmentValue

    return newAddress


def validatePositive( value, idText ) :
    """
    Test a value for positive integer, raising an exception if false.

    :param value: The value to be tested
    :param idText: Short text identifying the class of value for the exception
    """
    if (not isinstance( value, int )) \
            or (value < 0) :
        raise ConstraintError( idText + ' must be a positive integer' )


def validatePositiveNonZero( value, idText ) :
    """
    Test a value for positive, non-zero integer, raising an exception if false.

    :param value: The value to be tested
    :param idText: Short text identifying the class of value for the exception
    """
    if (not isinstance( value, int )) \
            or (value < 1) :
        raise ConstraintError( idText + ' must be a positive non-zero integer' )
