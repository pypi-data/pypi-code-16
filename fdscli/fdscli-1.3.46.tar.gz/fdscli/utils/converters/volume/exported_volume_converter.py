# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.volume.exported_volume import ExportedVolume

class ExportedVolumeConverter(object):
    '''Helper class for marshalling between ExportedVolume and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(exported_volume):
        '''
        Converts an ExportedVolume object into JSON format.
        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        exported_volume (ExportedVolume): Metadata for a volume exported to a bucket.

        Returns
        -------
        str : JSON formatted string
        '''
        d = dict()

        d["name"] = exported_volume.obj_prefix_key
        d["originalName"] = exported_volume.source_volume_name
        d["originalType"] = exported_volume.source_volume_type
        d["blobCount"] = str(exported_volume.blob_count)
        ctime = dict()
        ctime["seconds"] = exported_volume.creation_time
        ctime["nanos"] = 0

        d["dateCreated"] = ctime

        result = json.dumps(d)
        return result;

    @staticmethod
    def build_exported_volume_from_json(j_exported_volume):
        '''Produce a ``model.volume.ExportedVolume`` object from deserialized server response.

        Parameters
        ----------
        :type j_exported_volume: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type ``model.volume.ExportedVolume``
        '''
        exported_volume = ExportedVolume()

        # If given argument not a dict, decode to a dict
        if not isinstance(j_exported_volume, dict):
            j_exported_volume = json.loads(j_exported_volume)

        exported_volume.obj_prefix_key = j_exported_volume.pop( "name", 
            exported_volume.obj_prefix_key)
        exported_volume.source_volume_name = j_exported_volume.pop( "originalName",
            exported_volume.source_volume_name)
        exported_volume.source_volume_type = j_exported_volume.pop( "originalType",
            exported_volume.source_volume_type)
        exported_volume.blob_count = int(j_exported_volume.pop( "blobCount", 
            exported_volume.blob_count))

        ctime = j_exported_volume.pop( "dateCreated", 0 )
        exported_volume.creation_time = ctime["seconds"]

        return exported_volume

