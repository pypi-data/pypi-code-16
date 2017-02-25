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

import abc
import collections

from registerMap.exceptions import ConfigurationError


class ElementInterface :
    @abc.abstractproperty
    def startAddress( self ) :
        pass


    @abc.abstractproperty
    def endAddress( self ) :
        pass


    @abc.abstractproperty
    def sizeMemoryUnits( self ) :
        pass


class MemoryElement( ElementInterface ) :
    """
    Basic address and size properties of a memory element.
    """


    def __init__( self,
                  startAddress = None,
                  endAddress = None,
                  sizeMemoryUnits = None ) :
        self.__startAddress = startAddress

        if (endAddress is not None) and (sizeMemoryUnits is not None) :
            raise ConfigurationError( 'Cannot specify both endAddress and sizeMemoryUnits, '
                                      + repr( endAddress )
                                      + ', '
                                      + repr( sizeMemoryUnits ) )

        if startAddress is None :
            self.__endAddress = None
            self.__sizeMemoryUnits = 0
        else :
            # Assume the start address is numerical
            if endAddress is not None :
                self.__endAddress = endAddress
                self.__sizeMemoryUnits = self.__endAddress - self.startAddress + 1
            elif sizeMemoryUnits is not None :
                self.__sizeMemoryUnits = sizeMemoryUnits
                self.__endAddress = self.startAddress + self.__sizeMemoryUnits - 1
            else :
                # both endAddress and sizeMemoryUnits must be None
                self.__endAddress = self.__startAddress
                self.__sizeMemoryUnits = 1


    @property
    def startAddress( self ) :
        return self.__startAddress


    @startAddress.setter
    def startAddress( self, value ) :
        if value is None :
            self.__endAddress = value
        elif (self.__startAddress is None) and (self.__sizeMemoryUnits == 0) :
            # endAddress is implicitly None
            self.__endAddress = value
            self.__sizeMemoryUnits = 1
        elif (self.__startAddress is None) \
                and (self.__sizeMemoryUnits is not None) \
                and (self.__sizeMemoryUnits != 0) :
            # endAddress is implicitly None
            # sizeMemoryUnits is not None
            self.__endAddress = value + self.__sizeMemoryUnits - 1
        elif self.__endAddress is not None :
            # endAddress is numeric and be adjusted according to the startAddress change.
            # sizeMemoryUnits is unaffected.
            addressChange = value - self.__startAddress
            self.__endAddress += addressChange
        # else:
        # Since both endAddress and sizeMemoryUnits are None, we can only assign startAddress for use later when
        # endAddress or sizeMemoryUnits are known.
        self.__startAddress = value


    @property
    def endAddress( self ) :
        return self.__endAddress


    @endAddress.setter
    def endAddress( self, value ) :
        if self.__startAddress is None :
            raise ConfigurationError( 'Must define start address before attempting to define end address' )
        else :
            self.__endAddress = value
            self.__sizeMemoryUnits = self.__endAddress - self.__startAddress + 1


    @property
    def sizeMemoryUnits( self ) :
        return self.__sizeMemoryUnits


    @sizeMemoryUnits.setter
    def sizeMemoryUnits( self, value ) :
        self.__sizeMemoryUnits = value
        if (self.__startAddress is not None) \
                and (self.__sizeMemoryUnits is not None) :
            self.__endAddress = self.__startAddress + self.__sizeMemoryUnits - 1
        elif self.__sizeMemoryUnits is None :
            self.__endAddress = None


class ElementList( collections.OrderedDict ) :
    def __init__( self, owner ) :
        super( ).__init__( )
        self.__owner = owner


    def __setitem__( self, key, value ) :
        try :
            previousElementKey = next( reversed( self ) )
            previousElement = self[ previousElementKey ]
        except StopIteration as e :
            # This is the first register added.
            previousElement = self.__owner.firstElement

        super( ).__setitem__( key, value )

        value.previousElement = previousElement
        value.sizeChangeNotifier.addObserver( self.__owner.sizeObserver )
        # Address change of an element implies a potential size change to its owner.
        value[ 'constraints' ].addressChangeNotifier.addObserver( self.__owner.sizeObserver )
        value.reviewAddressChange( )
