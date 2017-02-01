# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

from fdscli.model.volume.settings.block_settings import BlockSettings
from fdscli.model.common.size import Size

class ISCSISettings(BlockSettings):
    '''Extends block settings by adding LUN and initiators data.

    Created on Nov 9, 2015
    
    @author: nate
    '''
    def __init__(self, capacity=None, block_size=None, encryption=False,
        compression=False, allow_mount=True, replica=False):

        # Default parameter values are evaluated once when the def statement
        # executes. Do not initialize objects in the def statement unless you
        # intentionally wish to refer to the same object everywhere.
        if capacity is None:
            capacity=Size(10, "GB")

        BlockSettings.__init__(self, capacity, block_size, encryption, compression,
            allow_mount, replica)
        self.type = "ISCSI"
        self.capacity = capacity
        self.block_size = block_size
        self.encryption = encryption
        self.compression = compression
        self.__incoming_credentials = []
        self.__outgoing_credentials = []
        self.__lun_permissions = []
        self.__initiators = []

    @property
    def incoming_credentials(self):
        return self.__incoming_credentials

    @incoming_credentials.setter
    def incoming_credentials(self, credentials):
        self.__incoming_credentials = credentials;

    @property
    def outgoing_credentials(self):
        return self.__outgoing_credentials

    @outgoing_credentials.setter
    def outgoing_credentials(self, credentials):
        self.__outgoing_credentials = credentials

    @property
    def lun_permissions(self):
        return self.__lun_permissions

    @lun_permissions.setter
    def lun_permissions(self, permissions):
        self.__lun_permissions = permissions
        
    @property
    def initiators(self):
        return self.__initiators
    
    @initiators.setter
    def initiators(self, some_initiators):
        self.__initiators = some_initiators
