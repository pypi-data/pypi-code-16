"""
Definition of Register
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

import collections
import logging
import math

import registerMap.elements.bitfield as rmf
import registerMap.elements.element as rml
import registerMap.elements.parameter as rmp
import registerMap.utility.observer as rmo
import registerMap.utility.yaml.encode as rye

# This is not used in this file, but should be retained to make BitRange accessible in this namespace
# to reduce imports for the user.
from registerMap.elements.bitfield import BitRange, BitField
from registerMap.exceptions import ConfigurationError, ConstraintError, ParseError


log = logging.getLogger( __name__ )


class Register :
    __defaultSize = 1
    __yamlName = 'register'


    class SizeChangeObserver( rmo.Observer ) :
        def __init__( self, owner ) :
            self.__owner = owner


        def update( self, observable, arguments ) :
            self.__owner.reviewSizeChange( )


    class AddressChangeObserver( rmo.Observer ) :
        def __init__( self, owner ) :
            self.__owner = owner


        def update( self, observable, arguments ) :
            # Register is only interested in the affect of address bits, memory unit bits or page size on its own
            # address from the memory space.
            # For constraints, Register is only interested in fixed address and alignment.
            # Ignore base address change which will be propagated from the previous register notification.
            if arguments not in [ 'baseAddress' ] :
                self.__owner.reviewAddressChange( )


    def __init__( self, memorySpace ) :
        self.addressChangeNotifier = rmo.Observable( )
        self.sizeChangeNotifier = rmo.Observable( )

        self.__addressObserver = Register.AddressChangeObserver( self )
        self.__element = rml.MemoryElement( )
        self.__memory = memorySpace
        self.__previousRegister = None
        self.__sizeObserver = Register.SizeChangeObserver( self )

        self.__data = {
            'bitFields' : BitFieldsParameter( ),
            'constraints' : rmp.ConstraintsParameter( self.__memory ),
            'description' : rmp.Parameter( 'description', '' ),
            'mode' : ModeParameter( 'rw' ),
            'name' : rmp.Parameter( 'name', None ),
            'public' : PublicParameter( True ),
            'summary' : rmp.Parameter( 'summary', '' )
        }

        self.__element.sizeMemoryUnits = 1
        self.__registerConstraintNotifiers( )


    def __registerConstraintNotifiers( self ) :
        self.__memory.addressChangeNotifier.addObserver( self.__addressObserver )
        self.__data[ 'constraints' ].value.addressChangeNotifier.addObserver( self.__addressObserver )
        self.__data[ 'constraints' ].value.sizeChangeNotifier.addObserver( self.__sizeObserver )


    def reviewSizeChange( self ) :
        newSize = self.__calculateSize( )
        if newSize != self.__element.sizeMemoryUnits :
            self.__element.sizeMemoryUnits = newSize
            self.sizeChangeNotifier.notifyObservers( )


    def reviewAddressChange( self ) :
        newStartAddress = self.__calculateStartAddress( )
        if newStartAddress != self.__element.startAddress :
            self.__element.startAddress = newStartAddress
            self.addressChangeNotifier.notifyObservers( )


    @property
    def address( self ) :
        """
        The first memory unit (the smallest numerical address value) used by the register.
        """
        return self.__element.startAddress


    @property
    def endAddress( self ) :
        """
        The last memory unit (the largest numerical address value) used by the register.
        """
        return self.__element.endAddress


    @property
    def memory( self ) :
        return self.__memory


    @property
    def previousElement( self ) :
        """
        The previous register from which to derive the address of the current register.
        """
        return self.__previousRegister


    @previousElement.setter
    def previousElement( self, previousRegister ) :
        self.__previousRegister = previousRegister
        self.__previousRegister.sizeChangeNotifier.addObserver( self.__addressObserver )
        self.__previousRegister.addressChangeNotifier.addObserver( self.__addressObserver )

        # An address or size change in the previous register can affect the address of the current register, but the
        # previous register should have no effect on the size of the current register which is determined by
        # constraints and bit fields.
        self.reviewAddressChange( )


    @property
    def sizeMemoryUnits( self ) :
        """
        The integer number of memory units used by the register.
        """
        return self.__element.sizeMemoryUnits


    def addBitField( self, name, bitRangeList ) :
        """
        :param name: Name of new bit field. Must be unique to the register the field is a member of, except special
        names 'reserved' and 'unassigned'.
        :param bitRange: Range of bits allocated to the new bit field.
        :return:
        """
        log.debug( "Add bit field, " + repr( name ) + ', ' + repr( bitRangeList ) )
        field = rmf.BitField( )

        field[ 'name' ] = name
        field[ 'bitRange' ].value = bitRangeList
        self.__validateBitField( name, field[ 'bitRange' ] )

        self.__data[ 'bitFields' ].value[ field[ 'name' ] ] = field

        log.debug( 'Subscribing to bit field changes, '
                   + repr( self.__data[ 'bitFields' ].value[ field[ 'name' ] ] )
                   + ', for '
                   + repr( self ) )
        self.__data[ 'bitFields' ].value[ field[ 'name' ] ].sizeChangeNotifier.addObserver( self.__sizeObserver )
        log.debug( 'Notifying on field change in register' )
        self.reviewSizeChange( )

        return self.__data[ 'bitFields' ].value[ field[ 'name' ] ]


    def __calculateStartAddress( self ) :
        if (self.__previousRegister is not None) and (self.__previousRegister.endAddress is not None) :
            # Page register impact is calculate before application of constraints. This means that constraints could
            # still affect the address. eg. if address alignment modified the affect of page register on the address.
            proposedAddress = self.__previousRegister.endAddress + 1
            initialAddress = self.__memory.calculatePageRegisterImpact( proposedAddress )
        else :
            initialAddress = None

        newAddress = self.__data[ 'constraints' ].value.applyAddressConstraints( initialAddress )
        return newAddress


    def __calculateSize( self ) :
        allBits = [ ]
        for thisField in self.__data[ 'bitFields' ].value.values( ) :
            if thisField[ 'bitRange' ].value is not None :
                allBits += thisField[ 'bitRange' ].value
        if len( allBits ) == 0 :
            size = self.__defaultSize
        else :
            size = math.ceil( max( allBits ) / self.__memory.memoryUnitBits )

        finalSize = self.__data[ 'constraints' ].value.applySizeConstraints( size )

        return finalSize


    def __validateBitField( self, name, bitRange ) :
        if self.bitFieldExists( name ) :
            raise ConfigurationError( 'Created bit field names must be unique, ' + name )

        if self.__anyOverlap( bitRange ) :
            raise ConfigurationError( 'Cannot have overlapping bit fields' )


    def __anyOverlap( self, bitRange ) :
        def inClosedInterval( value, interval ) :
            return (value >= min( interval )) and (value <= max( interval ))


        overlap = False
        rangeValue = bitRange.value
        for field in self.__data[ 'bitFields' ].value.values( ) :
            if (rangeValue is not None) \
                    and ((inClosedInterval( min( rangeValue ), field[ 'bitRange' ].value ))
                         or (inClosedInterval( max( rangeValue ), field[ 'bitRange' ].value ))) :
                overlap = True

        return overlap


    def bitFieldExists( self, name ) :
        bitFieldInData = name in self.__data[ 'bitFields' ].value

        return bitFieldInData


    def __getitem__( self, item ) :
        return self.__data[ item ].value


    def __setitem__( self, key, value ) :
        self.__data[ key ].validate( value )

        self.__data[ key ].value = value
        # Assume that any change events in bit fields or constraints will be taken care of using registered observers
        # of the relevant objects.


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace,
                       optional = False ) :
        def acquireBitFields( thisData ) :
            nonlocal register
            register.__data[ 'bitFields' ] = BitFieldsParameter.from_yamlData( thisData,
                                                                               optional = True )


        def acquireConstraints( thisData ) :
            nonlocal cls, memorySpace, register
            register.__data[ 'constraints' ] = rmp.ConstraintsParameter.from_yamlData( thisData, memorySpace,
                                                                                       optional = True )
            register.__registerConstraintNotifiers( )


        def acquireDescription( thisData ) :
            nonlocal register
            register.__data[ 'description' ] = rmp.Parameter.from_yamlData( thisData, 'description',
                                                                            optional = True )


        def acquireMode( thisData ) :
            nonlocal register
            register.__data[ 'mode' ] = ModeParameter.from_yamlData( thisData,
                                                                     optional = True )


        def acquireName( thisData ) :
            nonlocal register
            register.__data[ 'name' ] = rmp.Parameter.from_yamlData( thisData, 'name',
                                                                     optional = False )


        def acquirePublic( thisData ) :
            nonlocal register
            register.__data[ 'public' ] = PublicParameter.from_yamlData( thisData,
                                                                         optional = True )


        def acquireSummary( thisData ) :
            nonlocal register
            register.__data[ 'summary' ] = rmp.Parameter.from_yamlData( thisData, 'summary',
                                                                        optional = True )


        register = cls( memorySpace )
        if (not optional) and (cls.__yamlName not in yamlData.keys( )) :
            raise ConfigurationError( 'Register is not defined in yaml data' )
        elif cls.__yamlName in yamlData.keys( ) :
            acquireBitFields( yamlData[ cls.__yamlName ] )
            acquireConstraints( yamlData[ cls.__yamlName ] )
            acquireDescription( yamlData[ cls.__yamlName ] )
            acquireMode( yamlData[ cls.__yamlName ] )
            acquireName( yamlData[ cls.__yamlName ] )
            acquirePublic( yamlData[ cls.__yamlName ] )
            acquireSummary( yamlData[ cls.__yamlName ] )

        return register


    def to_yamlData( self ) :
        yamlData = { self.__yamlName : { } }

        parameters = list( )
        parameters.append( rye.parameter( '_address', self.address ) )
        parameters.append( rye.parameter( '_sizeMemoryUnits', self.sizeMemoryUnits ) )

        for parameterData in self.__data.values( ) :
            parameterYamlData = parameterData.to_yamlData( )
            parameters.append( parameterYamlData )

        for thisParameter in parameters :
            yamlData[ self.__yamlName ].update( thisParameter )

        return yamlData


class BitFieldsParameter( rmp.Parameter ) :
    __parameterName = 'bitFields'


    def __init__( self ) :
        super( ).__init__( self.__parameterName, collections.OrderedDict( ) )


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = False ) :
        parameter = cls( )
        if (not optional) and (cls.__parameterName not in yamlData.keys( )) :
            raise ConfigurationError( 'Bitfields not defined in yaml data' )
        elif cls.__parameterName in yamlData.keys( ) :
            for bitFieldYamlData in yamlData[ cls.__parameterName ] :
                bitField = rmf.BitField.from_yamlData( bitFieldYamlData )
                parameter.value[ bitField[ 'name' ] ] = bitField

        return parameter


    def to_yamlData( self ) :
        yamlData = { self.__parameterName : list( ) }

        for bitField in self.value.values( ) :
            yamlData[ self.__parameterName ].append( bitField.to_yamlData( ) )

        return yamlData


class ModeParameter( rmp.Parameter ) :
    # The default to_yamlData method implemented in Parameter is adequate for this child.
    validModes = [ 'ro', 'rw', 'wo', 'w1c', 'w0c' ]

    __parameterName = 'mode'


    def __init__( self,
                  value = 'rw' ) :
        super( ).__init__( self.__parameterName, value )
        self.validate( value )


    def validate( self, value ) :
        if value not in self.validModes :
            raise ConfigurationError(
                'Invalid value, ' + repr( value ) + ' valid value are, ' + repr( self.validModes ) )


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = False ) :
        parameter = super( ModeParameter, cls ).from_yamlData( yamlData, cls.__parameterName,
                                                               optional = optional )
        if optional and (parameter.value is None) :
            parameter.value = 'rw'
        elif not optional :
            parameter.validate( parameter.value )

        return parameter


class PublicParameter( rmp.Parameter ) :
    # The default to_yamlData method implemented in Parameter is adequate for this child.
    __parameterName = 'public'


    def __init__( self,
                  value = True ) :
        super( ).__init__( self.__parameterName, value )
        self.validate( value )


    def validate( self, value ) :
        if not isinstance( value, bool ) :
            raise ConfigurationError( 'Public must be specified as boolean' )


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = False ) :
        parameter = super( PublicParameter, cls ).from_yamlData( yamlData, cls.__parameterName,
                                                                 optional = optional )
        if optional and (parameter.value is None) :
            parameter.value = True
        elif not optional :
            parameter.validate( parameter.value )

        return parameter
