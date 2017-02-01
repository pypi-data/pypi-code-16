# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

from fdscli.model.volume.settings.volume_settings import VolumeSettings
from fdscli.model.common.size import Size

class ObjectSettings(VolumeSettings):
    '''Volume settings common for all object volume types.

    Created on May 29, 2015
    
    @author: nate
    '''

    def __init__(self, max_object_size=None, encryption=False, compression=False,
        allow_mount=True, replica=False):

        VolumeSettings.__init__(self, "OBJECT", encryption, compression, allow_mount, replica)
        self.type = "OBJECT"
        self.max_object_size = max_object_size
        self.encryption = encryption
        self.compression = compression

    @property
    def max_object_size(self):
        return self.__max_object_size
    
    @max_object_size.setter
    def max_object_size(self, size):
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

        self.__max_object_size = size
