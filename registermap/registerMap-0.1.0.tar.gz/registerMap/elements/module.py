"""
Definition of Module
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

import registerMap.elements.element as rml
import registerMap.elements.parameter as rmp
import registerMap.elements.register as rmr
import registerMap.utility.observer as rmo
import registerMap.utility.yaml.encode as rye

# This is not used in this file, but should be retained to make these elements accessible in this namespace
# to reduce imports for the user.
from registerMap.elements.memory import MemorySpace

from registerMap.exceptions import ConfigurationError, ParseError


log = logging.getLogger( __name__ )


class Module :
    __defaultSize = 0
    __yamlName = 'module'


    class AddressChangeObserver( rmo.Observer ) :
        def __init__( self, owner ) :
            self.__owner = owner


        def update( self, observable, arguments ) :
            self.__owner.reviewAddressChange( )


    def __init__( self, memorySpace ) :
        self.addressChangeNotifier = rmo.Observable( )
        self.sizeChangeNotifier = rmo.Observable( )

        self.__addressObserver = Module.AddressChangeObserver( self )

        self.__element = rml.MemoryElement( )
        self.__element.sizeMemoryUnits = 0

        self.__memory = memorySpace
        self.__previousModule = None

        self.__data = {
            'constraints' : rmp.ConstraintsParameter( self.__memory ),
            'description' : rmp.Parameter( 'description', '' ),
            'name' : rmp.Parameter( 'name', None ),
            'registers' : RegistersParameter( self ),
            'summary' : rmp.Parameter( 'summary', '' )
        }
        self.__sizeObserver = self.__data[ 'registers' ].sizeObserver

        self.__element.sizeMemoryUnits = None
        self.__registerConstraintNotifiers( )


    def __registerConstraintNotifiers( self ) :
        self.__memory.addressChangeNotifier.addObserver( self.__addressObserver )
        self.__data[ 'constraints' ].value.addressChangeNotifier.addObserver( self.__addressObserver )
        self.__data[ 'constraints' ].value.sizeChangeNotifier.addObserver( self.__sizeObserver )


    @property
    def assignedMemoryUnits( self ) :
        """
        :return: The number of memory units currently consumed by registers.
        """
        totalSize = 0
        for register in self.__data[ 'registers' ].value.values( ) :
            totalSize += register.sizeMemoryUnits

        return totalSize


    @property
    def baseAddress( self ) :
        """
        Address of the first register of the module (the "base" address of the module), or the fixed address if a
        'fixedAddress' constraint is applied.
        """
        return self.__element.startAddress


    @property
    def endAddress( self ) :
        return self.__element.endAddress


    @property
    def memory( self ) :
        """
        :return: Module local alias of for the memory space definitions of the register map.
        """
        return self.__memory


    @property
    def previousElement( self ) :
        """
        :return:
        """
        return self.__previousModule


    @previousElement.setter
    def previousElement( self, value ) :
        self.__previousModule = value
        # If the previous module changes address or size, then these events could both impact the address of the
        # current register.
        self.__previousModule.sizeChangeNotifier.addObserver( self.__addressObserver )
        self.__previousModule.addressChangeNotifier.addObserver( self.__addressObserver )

        self.reviewAddressChange( )


    @property
    def spanMemoryUnits( self ) :
        """
        :return: The current number of memory units spanned by the registers in the module.
        """
        return self.__element.sizeMemoryUnits


    @property
    def startAddress( self ) :
        return self.__element.startAddress


    def addRegister( self, name ) :
        """
        Create a new register of the specified name to be added to the module.

        :param name: Name of the register.
        :return: The added register.
        """
        register = rmr.Register( self.__memory )
        register[ 'name' ] = name
        self.__validateAddedRegister( register )

        self.__data[ 'registers' ].value[ register[ 'name' ] ] = register

        log.debug( 'Notifying on register change in module' )
        self.reviewSizeChange( )

        return register


    def __validateAddedRegister( self, register ) :
        foundRegisters = [ x[ 'name' ] for x in self.__data[ 'registers' ].value.values( ) if
                           x[ 'name' ] == register[ 'name' ] ]

        if len( foundRegisters ) != 0 :
            raise ConfigurationError(
                'Created register names must be unique within a module, ' + repr( register[ 'name' ] ) )


    def reviewSizeChange( self ) :
        newSpan = self.__calculateSpan( )
        if newSpan != self.__element.sizeMemoryUnits :
            self.__element.sizeMemoryUnits = newSpan
            self.sizeChangeNotifier.notifyObservers( )


    def reviewAddressChange( self ) :
        def updateFirstRegister( ) :
            nonlocal self

            if self.__data[ 'registers' ].firstElement is not None :
                self.__data[ 'registers' ].firstElement.endAddress = newStartAddress - 1


        def updateSpan( ) :
            nonlocal self

            newSpan = self.__calculateSpan( )
            if newSpan != self.__element.sizeMemoryUnits :
                self.__element.sizeMemoryUnits = newSpan
                self.sizeChangeNotifier.notifyObservers( )


        newStartAddress = self.__calculateStartAddress( )
        if newStartAddress != self.__element.startAddress :
            self.__element.startAddress = newStartAddress
            updateFirstRegister( )
            updateSpan( )

            self.addressChangeNotifier.notifyObservers( )


    def __calculateStartAddress( self ) :
        if (self.__previousModule is not None) and (self.__previousModule.endAddress is not None) :
            # Page register impact is calculate before application of constraints. This means that constraints could
            # still affect the address. eg. if address alignment modified the affect of page register on the address.
            proposedAddress = self.__previousModule.endAddress + 1
            initialAddress = self.__memory.calculatePageRegisterImpact( proposedAddress )
        else :
            initialAddress = None

        newAddress = self.__data[ 'constraints' ].value.applyAddressConstraints( initialAddress )
        return newAddress


    def __calculateSpan( self ) :
        def sizeCalculationWithAddresses( ) :
            nonlocal self

            # Module size is the difference between the address of the first memory unit and the last memory unit consumed by the last register
            startAddress = self.__element.startAddress
            endAddress = startAddress

            if len( self.__data[ 'registers' ].value ) == 0 :
                totalRegisterSpan = 0
            else :
                for register in self.__data[ 'registers' ].value.values( ) :
                    if (register.endAddress is not None) and (register.endAddress > endAddress) :
                        endAddress = register.endAddress
                    elif register.endAddress is None :
                        log.debug(
                            'Register has None end address during span calculation, ' + repr( register[ 'name' ] ) )

                totalRegisterSpan = endAddress - startAddress + 1

            return totalRegisterSpan


        if self.__element.startAddress is not None :
            moduleSize = sizeCalculationWithAddresses( )
        else :
            moduleSize = None

        finalSize = self.__data[ 'constraints' ].value.applySizeConstraints( moduleSize )

        return finalSize


    def __getitem__( self, item ) :
        return self.__data[ item ].value


    def __setitem__( self, key, value ) :
        self.__data[ key ].value = value
        # Assume that any change events in registers or constraints will be taken care of using registered observers of
        # the relevant objects.


    @classmethod
    def from_yamlData( cls, yamlData, memorySpace,
                       optional = False ) :

        def acquireConstraints( thisData ) :
            nonlocal module
            module.__data[ 'constraints' ] = rmp.ConstraintsParameter.from_yamlData( thisData, module.__memory,
                                                                                     optional = True )
            module.__registerConstraintNotifiers( )


        def acquireDescription( thisData ) :
            nonlocal module
            module.__data[ 'description' ] = rmp.Parameter.from_yamlData( thisData, 'description',
                                                                          optional = True )


        def acquireName( thisData ) :
            nonlocal module
            module.__data[ 'name' ] = rmp.Parameter.from_yamlData( thisData, 'name',
                                                                   optional = False )


        def acquireRegisters( thisData ) :
            nonlocal module
            module.__data[ 'registers' ] = RegistersParameter.from_yamlData( thisData, module, module.__memory,
                                                                             optional = True )


        def acquireSummary( thisData ) :
            nonlocal module
            module.__data[ 'summary' ] = rmp.Parameter.from_yamlData( thisData, 'summary',
                                                                      optional = True )


        module = cls( memorySpace )
        if (not optional) and (cls.__yamlName not in yamlData.keys( )) :
            raise ParseError( 'Module is not defined in yaml data' )
        elif cls.__yamlName in yamlData.keys( ) :
            acquireConstraints( yamlData[ cls.__yamlName ] )
            acquireDescription( yamlData[ cls.__yamlName ] )
            acquireName( yamlData[ cls.__yamlName ] )
            acquireRegisters( yamlData[ cls.__yamlName ] )
            acquireSummary( yamlData[ cls.__yamlName ] )

        return module


    def to_yamlData( self ) :
        yamlData = { self.__yamlName : { } }

        parameters = list( )
        parameters.append( rye.parameter( '_address', self.baseAddress ) )
        parameters.append( rye.parameter( '_spanMemoryUnits', self.spanMemoryUnits ) )

        for parameterData in self.__data.values( ) :
            parameterYamlData = parameterData.to_yamlData( )
            parameters.append( parameterYamlData )

        for thisParameter in parameters :
            yamlData[ self.__yamlName ].update( thisParameter )

        return yamlData


class RegistersParameter( rmp.Parameter ) :
    __parameterName = 'registers'


    class FirstRegister :
        def __init__( self,
                      endAddress = None ) :
            self.addressChangeNotifier = rmo.Observable( )
            self.sizeChangeNotifier = rmo.Observable( )

            self.__endAddress = endAddress


        @property
        def endAddress( self ) :
            return self.__endAddress


        @endAddress.setter
        def endAddress( self, value ) :
            self.__endAddress = value
            self.sizeChangeNotifier.notifyObservers( )


    class SizeChangeObserver( rmo.Observer ) :
        def __init__( self, owner ) :
            self.__owner = owner


        def update( self, observable, arguments ) :
            self.__owner.reviewSizeChange( )


    def __init__( self, owner ) :
        super( ).__init__( self.__parameterName, rml.ElementList( self ) )

        self.__owner = owner

        self.firstElement = None
        self.sizeObserver = RegistersParameter.SizeChangeObserver( self.__owner )

        self.__createFirstRegisterPrevious( )


    def __createFirstRegisterPrevious( self ) :
        if self.__owner.baseAddress is None :
            # Have to deal with None addresses as a special case
            thisEndAddress = None
        else :
            thisEndAddress = (self.__owner.startAddress - 1)

        self.firstElement = RegistersParameter.FirstRegister( endAddress = thisEndAddress )


    @classmethod
    def from_yamlData( cls, yamlData, owner, memorySpace,
                       optional = False ) :
        parameter = cls( owner )
        if (not optional) and (cls.__parameterName not in yamlData.keys( )) :
            raise ParseError( 'Registers not defined in yaml data' )
        elif cls.__parameterName in yamlData.keys( ) :
            for registerYamlData in yamlData[ cls.__parameterName ] :
                register = rmr.Register.from_yamlData( registerYamlData, memorySpace )
                parameter.value[ register[ 'name' ] ] = register

        return parameter


    def to_yamlData( self ) :
        yamlData = { self.__parameterName : list( ) }

        for register in self.value.values( ) :
            yamlData[ self.__parameterName ].append( register.to_yamlData( ) )

        return yamlData
