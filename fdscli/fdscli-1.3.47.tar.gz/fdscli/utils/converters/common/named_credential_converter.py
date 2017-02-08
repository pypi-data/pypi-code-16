# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.common.s3credentials import S3Credentials

class NamedCredentialConverter(object):
    '''Helper class for marshalling between NamedCredential class and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(named_credential):
        '''Converts a named credential object into a JSON formatted string.

        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        :type named_credential: ``model.common.NamedCredential``
        :param named_credential: A named credential object

        Returns
        -------
        :type string
        '''
        d = dict()

        if named_credential.bucketname is not None:
            s3 = dict()
            if (named_credential.digest is not None and named_credential.digest != ""):
                s3["digest"] = named_credential.digest
            s3["userId"] = named_credential.user_id
            s3["name"] = named_credential.name
            if (named_credential.bucketname is not None and named_credential.bucketname != ""):
                s3["bucketName"] = named_credential.bucketname
            s3["url"] = named_credential.url
            s3["accessKey"] = named_credential.s3credentials.access_key_id
            s3["secretKey"] = named_credential.s3credentials.secret_key
            d["s3"] = s3
        else:
            f1 = dict()
            if (named_credential.digest is not None and named_credential.digest != ""):
                f1["digest"] = named_credential.digest
            f1["userId"] = named_credential.user_id
            f1["name"] = named_credential.name
            f1["omUrl"] = named_credential.url
            f1["protocol"] = named_credential.protocol
            f1["username"] = named_credential.username
            f1["password"] = named_credential.password
            f1["hostname"] = named_credential.hostname
            f1["port"] = named_credential.port
            d["f1"] = f1

        result = json.dumps(d)
        return result

    @staticmethod
    def build_from_json(j_str):
        '''Produces a ``model.common.NamedCredential`` object from deserialized server response

        Parameters
        ----------
        :type j_str: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type ``model.common.NamedCredential``
        '''
        named_credential = NamedCredential()

        # If given argument not a dict, decode to a dict
        if not isinstance(j_str, dict):
            j_str = json.loads(j_str)

        if "s3" in j_str:
            s3 = json.dumps(j_str.pop("s3"))
            s3 = json.loads(s3)
            named_credential.digest = s3.pop("digest", named_credential.digest)
            named_credential.user_id = s3.pop("userId", named_credential.user_id)
            named_credential.name = s3.pop("name", named_credential.name)
            named_credential.bucketname = s3.pop("bucketName", named_credential.bucketname)
            named_credential.url = s3.pop("url", named_credential.url)
            named_credential.s3credentials = S3Credentials()
            named_credential.s3credentials.access_key_id = s3.pop("accessKey", named_credential.s3credentials.access_key_id)
            named_credential.s3credentials.secret_key = s3.pop("secretKey", named_credential.s3credentials.secret_key)

        elif "f1" in j_str:
            f1 = json.dumps(j_str.pop("f1"))
            f1 = json.loads(f1)
            named_credential.digest = f1.pop("digest", named_credential.digest)
            named_credential.user_id = f1.pop("userId", named_credential.user_id)
            named_credential.name = f1.pop("name", named_credential.name)
            named_credential.url = f1.pop("omUrl", named_credential.url)
            named_credential.username = f1.pop("username", named_credential.username)
            named_credential.protocol = f1.pop("protocol", named_credential.protocol)
            named_credential.hostname = f1.pop("hostname", named_credential.hostname)
            named_credential.password = f1.pop("password", named_credential.password)
            named_credential.port = int(f1.pop("port", named_credential.port))

        return named_credential
