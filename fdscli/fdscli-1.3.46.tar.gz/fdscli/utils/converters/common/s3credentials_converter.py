#
# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.common.s3credentials import S3Credentials

class S3CredentialsConverter(object):
    '''Helper class for marshalling between S3Credential class and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(credentials):
        '''
        Converts S3 credentials object into JSON format. We presume that the recipient (a server)
        uses a package like Gson and passes the type literal when deserializing the JSON formatted
        string.

        Parameters
        ----------
        credentials (S3Credentials) : Credentials for accessing simple storage services.

        Returns
        -------
        str : JSON formatted string
        '''
        j_str = dict()
        
        j_str["accessKey"] = credentials.access_key_id
        j_str["secretKey"] = credentials.secret_key
        
        j_str = json.dumps(j_str)
        
        return j_str
    
    @staticmethod
    def build_s3_credentials_from_json(j_credentials):
        '''
        Converts dictionary or JSON formatted string into S3Credentials object.

        Parameters
        ----------
        j_credentials (str | dict)

        Returns
        -------
        S3Credentials
        '''
        s3credentials = S3Credentials()
        
        if not isinstance(j_credentials, dict):
            j_credentials  = json.loads(j_credentials)
        
        s3credentials.access_key_id = j_credentials.pop("accessKey", s3credentials.access_key_id)
        s3credentials.secret_key = j_credentials.pop("secretKey", s3credentials.secret_key)
        
        return s3credentials
