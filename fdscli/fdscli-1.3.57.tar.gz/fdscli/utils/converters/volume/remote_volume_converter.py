#
# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.volume.remote_volume import RemoteVolume
from fdscli.utils.converters.volume.volume_converter import VolumeConverter

class RemoteVolumeConverter(object):
    '''Helper class for marshalling between RemoteVolume and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(remote_volume):
        '''
        Converts a RemoteVolume object into JSON format.
        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        remote_volume (RemoteVolume): The combination of volume data, source volume name,
            and an OM service locator.

        Returns
        -------
        str : JSON formatted string
        '''
        j_v = VolumeConverter.to_json(remote_volume.volume)

        # Purposefully flattens the object
        d = None
        if not isinstance(j_v, dict):
            d = json.loads(j_v)
        else:
            d = j_v

        d["remoteOmUrl"] = remote_volume.remote_om_url
        d["originalVolumeName"] = remote_volume.source_volume_name

        result = json.dumps(d)
        return result;

    @staticmethod
    def build_remote_volume_from_json(j_remote_volume):
        '''
        Converts dictionary or JSON formatted string into an RemoteVolume object.

        Parameters
        ----------
        j_remote_volume (str | dict)

        Returns
        -------
        RemoteVolume
        '''
        remote_volume = RemoteVolume()

        if not isinstance(j_remote_volume, dict):
            j_remote_volume = json.loads(j_remote_volume)

        remote_volume.remote_om_url = j_remote_volume.pop( "remoteOmUrl", 
            remote_volume.remote_om_url)
        remote_volume.source_volume_name = j_remote_volume.pop( "originalVolumeName", 
            remote_volume.source_volume_name)
        remote_volume.volume = VolumeConverter.build_volume_from_json(j_remote_volume)

        return remote_volume

