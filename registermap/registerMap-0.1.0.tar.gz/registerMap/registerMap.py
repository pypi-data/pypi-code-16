"""
Definition of RegisterMap
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

import registerMap.elements.element as rml
import registerMap.elements.memory as rmm
import registerMap.elements.module as rmd
import registerMap.elements.parameter as rmp

# This is not used in this file, but should be retained to make these elements accessible in this namespace
# to reduce imports for the user.
from registerMap.elements.module import *

from registerMap.exceptions import ConstraintError, ConfigurationError


class RegisterMap :
    __yamlName = 'registerMap'


    class AddressChangeObserver( rmo.Observer ) :
        def __init__( self, owner ) :
            self.__owner = owner


        def update( self, source, arguments ) :
            self.__owner.reviewAddressChange( )


    def __init__( self ) :
        self.__addressObserver = RegisterMap.AddressChangeObserver( self )

        self.__initializeMemorySpace( )
        self.__initializeElement( )

        self.__data = {
            'description' : rmp.Parameter( 'description', '' ),
            'modules' : ModulesParameter( self ),
            'summary' : rmp.Parameter( 'summary', '' )
        }
        self.__sizeObserver = self.__data[ 'modules' ].sizeObserver
        self.__memorySpace.sizeChangeNotifier.addObserver( self.__sizeObserver )


    def __initializeElement( self ) :
        self.__element = rml.MemoryElement( )
        self.__element.startAddress = self.__memorySpace.baseAddress
        self.__element.sizeMemoryUnits = None


    def __initializeMemorySpace( self ) :
        self.__memorySpace = rmm.MemorySpace( )
        self.__memorySpace.addressChangeNotifier.addObserver( self.__addressObserver )


    @property
    def assignedMemoryUnits( self ) :
        """
        :return: Total number of memory units assigned a definition via a register.
        """
        totalSize = 0
        for thisModule in self.__data[ 'modules' ].value.values( ) :
            totalSize += thisModule.assignedMemoryUnits

        return totalSize


    @property
    def memory( self ) :
        return self.__memorySpace


    @property
    def spanMemoryUnits( self ) :
        return self.__element.sizeMemoryUnits


    @property
    def startAddress( self ) :
        return self.__element.startAddress


    def addModule( self, name ) :
        """
        Create a module with the specified name.

        :param name: Name of the new module.

        :return: The created module.
        """
        thisModule = rmd.Module( self.__memorySpace )
        thisModule[ 'name' ] = name
        self.__validateAddedModule( thisModule )

        self.__data[ 'modules' ].value[ thisModule[ 'name' ] ] = thisModule

        log.debug( 'Notifying on module change in register map' )
        self.reviewSizeChange( )

        return thisModule


    def __validateAddedModule( self, module ) :
        foundModules = [ x[ 'name' ] for x in self.__data[ 'modules' ].value.values( ) if
                         x[ 'name' ] == module[ 'name' ] ]

        if len( foundModules ) != 0 :
            raise ConfigurationError(
                'Created module names must be unique within a register map, ' + repr( module[ 'name' ] ) )


    def reviewAddressChange( self ) :
        """
        Propagate a memory space base address change.
        """
        if self.__data[ 'modules' ].firstElement is not None :
            self.__data[ 'modules' ].firstElement.endAddress = self.__memorySpace.baseAddress - 1


    def reviewSizeChange( self ) :
        startAddress = self.__memorySpace.baseAddress
        endAddress = startAddress
        registersCreated = False
        for thisModule in self.__data[ 'modules' ].value.values( ) :
            if thisModule.endAddress > endAddress :
                endAddress = thisModule.endAddress

            if len( thisModule[ 'registers' ] ) > 0 :
                registersCreated = True

        if (endAddress == startAddress) and (not registersCreated) :
            self.__element.sizeMemoryUnits = 0
        elif (endAddress == startAddress) and registersCreated :
            self.__element.sizeMemoryUnits = 1
        else :
            self.__element.sizeMemoryUnits = endAddress - startAddress


    def __getitem__( self, item ) :
        return self.__data[ item ].value


    def __setitem__( self, key, value ) :
        self.__data[ key ].value = value


    @classmethod
    def from_yamlData( cls, yamlData,
                       optional = False ) :
        def acquireMemorySpace( thisData ) :
            nonlocal thisMap
            thisMap.__memorySpace = rmm.MemorySpace.from_yamlData( thisData )
            thisMap.__memorySpace.sizeChangeNotifier.addObserver( thisMap.__sizeObserver )
            thisMap.__memorySpace.addressChangeNotifier.addObserver( thisMap.__addressObserver )


        def acquireDescription( thisData ) :
            nonlocal thisMap
            thisMap.__data[ 'description' ] = rmp.Parameter.from_yamlData( thisData, 'description',
                                                                           optional = True )


        def acquireModules( thisData ) :
            nonlocal thisMap
            thisMap.__data[ 'modules' ] = ModulesParameter.from_yamlData( thisData, thisMap, thisMap.__memorySpace,
                                                                          optional = True )


        def acquireSummary( thisData ) :
            nonlocal thisMap
            thisMap.__data[ 'summary' ] = rmp.Parameter.from_yamlData( thisData, 'summary',
                                                                       optional = True )


        thisMap = cls( )
        if (not optional) and (cls.__yamlName not in yamlData.keys( )) :
            raise ParseError( 'RegisterMap is not defined in yaml data' )
        elif cls.__yamlName in yamlData.keys( ) :
            # Memory space acquisition must occur first because it is used by module acquisition
            acquireMemorySpace( yamlData[ cls.__yamlName ] )

            acquireDescription( yamlData[ cls.__yamlName ] )
            acquireSummary( yamlData[ cls.__yamlName ] )

            acquireModules( yamlData[ cls.__yamlName ] )

            thisMap.reviewAddressChange( )
            thisMap.reviewSizeChange( )

        return thisMap


    def to_yamlData( self ) :
        yamlData = { self.__yamlName : { } }

        parameters = list( )
        for parameterData in self.__data.values( ) :
            parameterYamlData = parameterData.to_yamlData( )
            parameters.append( parameterYamlData )

        yamlData[ self.__yamlName ].update( self.__memorySpace.to_yamlData( ) )
        for thisParameter in parameters :
            yamlData[ self.__yamlName ].update( thisParameter )

        return yamlData


class ModulesParameter( rmp.Parameter ) :
    __parameterName = 'modules'


    class FirstModule :
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


        def update( self, source, arguments ) :
            self.__owner.reviewSizeChange( )


    def __init__( self, owner ) :
        super( ).__init__( self.__parameterName, rml.ElementList( self ) )

        self.__owner = owner

        self.firstElement = None
        self.sizeObserver = ModulesParameter.SizeChangeObserver( self.__owner )

        self.__createFirstModulePrevious( )


    def __createFirstModulePrevious( self ) :
        assert self.__owner.memory.baseAddress >= 0
        firstModule = ModulesParameter.FirstModule( endAddress = (self.__owner.memory.baseAddress - 1) )

        self.firstElement = firstModule


    @classmethod
    def from_yamlData( cls, yamlData, owner, memorySpace,
                       optional = False ) :
        parameter = cls( owner )
        if (not optional) and (cls.__parameterName not in yamlData.keys( )) :
            raise ParseError( 'Modules not defined in yaml data' )
        elif cls.__parameterName in yamlData.keys( ) :
            for moduleYamlData in yamlData[ cls.__parameterName ] :
                module = rmd.Module.from_yamlData( moduleYamlData, memorySpace )
                parameter.value[ module[ 'name' ] ] = module

        return parameter


    def to_yamlData( self ) :
        yamlData = { self.__parameterName : list( ) }

        for register in self.value.values( ) :
            yamlData[ self.__parameterName ].append( register.to_yamlData( ) )

        return yamlData
