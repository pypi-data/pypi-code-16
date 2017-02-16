# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
class ExportedVolume(object):
    '''Metadata for a volume exported to a bucket.

    Since the exported volume is serialized, a bucket read is required to get metadata.

    Attributes
    ----------
    :type __obj_prefix_key: str
    :attr __obj_prefix_key: Uniquely identifies the exported volume in the bucket.

    :type __source_domain_id: long
    :attr __source_domain_id: Unique identifier for the original, source domain

    :type __source_volume_id: long
    :attr __source_volume_id: Unique identifier for the original, source volume

    :type __source_snapshot_id: long
    :attr __source_snapshot_id: Unique identifier for the original, source snapshot
        Equals zero if the exported volume is not an exported snapshot.

    :type __source_volume_name: str
    :attr __source_volume_name: Name of the original, source volume.

    :type __source_volume_type: str
    :attr __source_volume_type: One of BLOCK, OBJECT, NFS, or ISCSI

    :type __creation_time: long
    :type __creation_time: Creation time for the original, source volume
        TODO: Is that right? Or is it creation time for the xvol?

    :type __blob_count: int
    :attr __blob_count: Blob count for the original, source volume
    '''

    def __init__(self, obj_prefix_key=None, source_volume_name=None,
        source_volume_type="OBJECT", creation_time=0, blob_count=0):

        self.obj_prefix_key = obj_prefix_key
        self.source_volume_name = source_volume_name
        self.source_volume_type = source_volume_type
        self.creation_time = creation_time
        self.blob_count = blob_count

    @property
    def obj_prefix_key(self):
        return self.__obj_prefix_key

    @obj_prefix_key.setter
    def obj_prefix_key(self, obj_prefix_key):
        self.__obj_prefix_key = obj_prefix_key

        # The object prefix key is encoded.
        self.decode_obj_prefix_key(obj_prefix_key)

    @property
    def source_domain_id(self):
        return self.__source_domain_id

    @source_domain_id.setter
    def source_domain_id(self, source_domain_id):
        self.__source_domain_id = long(source_domain_id)

    @property
    def source_snapshot_id(self):
        return self.__source_snapshot_id

    @source_snapshot_id.setter
    def source_snapshot_id(self, source_snapshot_id):
        self.__source_snapshot_id = long(source_snapshot_id)

    @property
    def source_volume_id(self):
        return self.__source_volume_id

    @source_volume_id.setter
    def source_volume_id(self, source_volume_id):
        self.__source_volume_id = long(source_volume_id)

    @property
    def source_volume_name(self):
        return self.__source_volume_name

    @source_volume_name.setter
    def source_volume_name(self, source_volume_name):
        self.__source_volume_name = source_volume_name

    @property
    def source_volume_type(self):
        return self.__source_volume_type

    @source_volume_type.setter
    def source_volume_type(self, source_volume_type):
        self.__source_volume_type = source_volume_type

    @property
    def creation_time(self):
        return self.__creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        self.__creation_time = long(creation_time)

    @property
    def blob_count(self):
        return self.__blob_count

    @blob_count.setter
    def blob_count(self, blob_count):
        self.__blob_count = blob_count

    def decode_obj_prefix_key(self, key):
        '''Parses the object prefix key and sets source domain, snapshot, and volume Ids.
        '''
        self.source_domain_id = 0
        self.source_snapshot_id = 0
        self.source_volume_id = 0

        if key is None:
            return

        # The delimiter for a S3 object prefix key is forward-slash.
        parts = [x.strip() for x in key.split("/")]

        if len(parts) < 3:
            return

        # Object prefix keys are versioned for exported volumes.
        # There is no version 1.
        version = 0
        if len(parts) == 5:
            version = int(parts[0])

        if version == 0:
            self.source_domain_id = parts[0]
            self.source_volume_id = parts[1]

        elif version == 2:
            self.source_domain_id = parts[1]
            self.source_volume_id = parts[2]
            self.source_snapshot_id = parts[3]

