# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

from fdscli.model.volume.settings.volume_settings import VolumeSettings
from fdscli.model.common.size import Size

class BlockSettings(VolumeSettings):
    '''Volume settings common for all block volume types.

    Expected to have subclasses.
    '''

    def __init__(self, capacity=None, block_size=None, encryption=False,
        compression=False, allow_mount=True, replica=False):

        # Default parameter values are evaluated once when the def statement
        # executes. Do not initialize objects in the def statement unless you
        # intentionally wish to refer to the same object everywhere.
        if capacity is None:
            capacity=Size(10, "GB")

        VolumeSettings.__init__(self, "BLOCK", encryption, compression, allow_mount, replica)
        self.type = "BLOCK"
        self.capacity = capacity
        self.block_size = block_size
        self.encryption = encryption
        self.compression = compression

    @property
    def capacity(self):
        return self.__capacity
    
    @capacity.setter
    def capacity(self, size):
        '''
        Parameters
        ----------
        :type size: ``model.common.Size``
        :param size: Logical bytes with units
        '''
        # Use duck-typing
        if size is not None:
            if (not hasattr(size, 'size')) and (not hasattr(size, 'unit')):
                raise TypeError("Expected a size with units.")

        self.__capacity = size
        
    @property
    def block_size(self):
        return self.__block_size
    
    @block_size.setter
    def block_size(self, size):
        '''
        Parameters
        ----------
        :type size: ``model.common.Size``
        :param size: Logical bytes with units
        '''
        # Use duck-typing
        if size is not None:
            if (not hasattr(size, 'size')) and (not hasattr(size, 'unit')):
                raise TypeError("Expected a size with units.")

        self.__block_size = size

