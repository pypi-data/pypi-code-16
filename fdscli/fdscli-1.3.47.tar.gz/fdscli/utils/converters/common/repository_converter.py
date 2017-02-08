#
# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.common.repository import Repository
from fdscli.utils.converters.common.s3credentials_converter import S3CredentialsConverter

class RepositoryConverter(object):
    '''Helper class for marshalling between Repository class and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(repository):
        '''
        Converts a repository object into JSON format. The recipient knows what kind of repository
        is expected from the context of the REST call. We presume that the recipient (a server)
        uses a package like Gson and passes the type literal when deserializing the JSON formatted
        string.

        Parameters
        ----------
        repository (Repository) : A repository object that specifies credentials and storage
            endpoint 

        Returns
        -------
        str : JSON formatted string
        '''
        d = dict()

        if repository.credentials is not None:
            j_credentials = S3CredentialsConverter.to_json(repository.credentials)
            d["s3Credentials"] = json.loads(j_credentials)

        # S3 endpoint or Xdi endpoint
        d["url"] = repository.url
        d["uuid"] = repository.uuid
        d["volumeId"] = repository.volume_id

        if repository.bucket_name is not None:
            d["s3Bucket"] = repository.bucket_name
            if repository.new_volume_name is not None:
                d["importedVolumeName"] = repository.new_volume_name
            # For list exports, object prefix key is unspecified
            if repository.obj_prefix_key is not None:
                d["objectPrefixKey"] = repository.obj_prefix_key
        else:
            d["omUrl"] = repository.remote_om
            d["volumeName"] = repository.remote_volume_name

        result = json.dumps(d)
        
        return result
    
    @staticmethod
    def build_repository_from_json(j_repository):
        '''
        Converts dictionary or JSON formatted string into a Repository object.

        Parameters
        ----------
        j_repository (str | dict)

        Returns
        -------
        Repository
        '''
        repository = Repository()
        
        if not isinstance(j_repository, dict):
            j_repository = json.loads(j_repository)

        # When repository corresponds to remote volume, there are no S3 credentials
        if "s3Credentials" in j_repository:
            repository.credentials = S3CredentialsConverter.build_s3_credentials_from_json(
                j_repository.pop("s3Credentials"))

        # S3 endpoint or Xdi endpoint
        repository.url = j_repository.pop( "url", repository.url )
        repository.uuid = j_repository.pop( "uuid", repository.uuid )
        repository.volume_id = long(j_repository.pop( "volumeId", repository.volume_id ))
        repository.bucket_name = j_repository.pop( "s3Bucket", repository.bucket_name )

        if repository.bucket_name is not None:
            repository.obj_prefix_key = j_repository.pop( "objectPrefixKey", repository.obj_prefix_key )
            repository.new_volume_name = j_repository.pop( "importedVolumeName", repository.new_volume_name )
        else:
            repository.remote_om = j_repository.pop( "omUrl", repository.url )
            repository.remote_volume_name = j_repository.pop( "volumeName", repository.remote_volume_name )

        return repository
