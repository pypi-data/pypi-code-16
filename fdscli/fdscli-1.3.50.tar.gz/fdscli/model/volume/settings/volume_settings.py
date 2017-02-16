# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#
class VolumeSettings(object):
    '''Settings common to all volume types.

    Created on May 29, 2015
    
    @author: nate
    '''

    def __init__(self, a_type="OBJECT", encryption=False, compression=False,
        allow_mount=True, replica=False):

        self.type = a_type
        self.encryption = encryption
        self.compression = compression
        self.allow_mount = allow_mount
        self.replica = replica

    @property
    def type(self):
        return self.__type
    
    @type.setter
    def type(self, a_type):
        
        if a_type not in ("OBJECT", "BLOCK", "ISCSI", "NFS"):
            raise TypeError()
        
        self.__type = a_type

    def __convert_to_bool(self, value):
        if type( value ) is bool:
            return value

        if value.lower() in ( "true", "yes", "y", "t" ):
            return True

        return False

    @property
    def allow_mount(self):
        return self.__allow_mount

    @allow_mount.setter
    def allow_mount(self, allow_mount):
        self.__allow_mount = self.__convert_to_bool(allow_mount)

    @property
    def encryption(self):
        return self.__encryption

    @encryption.setter
    def encryption(self, encryption):
        self.__encryption = self.__convert_to_bool(encryption)

    @property
    def compression(self):
        return self.__compression

    @compression.setter
    def compression(self, compression):
        self.__compression = self.__convert_to_bool(compression)

    @property
    def replica(self):
        return self.__replica

    @replica.setter
    def replica(self, replica):
        self.__replica = self.__convert_to_bool(replica)

