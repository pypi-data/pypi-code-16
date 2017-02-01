# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
from fdscli.model.common.s3credentials import S3Credentials

class NamedCredential(object): 
    '''Specifies the URL of a data storage endpoint and credentials required to access the data.

    Attributes
    ----------
    :type __digest: string
    :attr __digest: Hash value that uniquely identifies the named credential

    :type __user_id: int
    :attr __user_id: Unique identifier for a Formation user

    :type __name: string
    :attr __name: Customer or system assigned name, unique for a given user

    :type __url: string
    :attr __url: S3 endpoint or remote OM. Like ``https://s3-us-west2.amazonaws.com`` or
        ``https://remoteOMUser:secret@remoteOMHost:remoteOMPort``.

    :type __bucketname: string
    :attr __bucketname: Optional bucket name

    :type __s3credentials: ``model.common.S3Credentials``
    :attr __s3credentials: Optional access key and secret key for S3 endpoint

    :type __protocol: string
    :attr __protocol: For F1 named credential, the protocol

    :type __username: string
    :attr __username: For F1 named credential, user name for remote OM

    :type __password: string
    :attr __password: For F1 named credential, the password for remote OM

    :type __hostname: string
    :attr __hostname: For F1 named credential, the hostname for remote OM

    :type __port: int
    :attr __port: For F1 named credential, the port for remote OM
    '''

    def __init__(self, digest=None, user_id=None, name=None, s3credentials=None):

        self.digest = digest
        self.user_id = user_id
        self.name = name
        self.url = None
        self.s3credentials = s3credentials
        if self.s3credentials is None:
            self.s3credentials = S3Credentials()
        self.bucketname = None
        self.protocol = None
        self.username = None
        self.password = None
        self.hostname = None
        self.port = 0

    @property
    def digest(self):
        return self.__digest
    
    @digest.setter
    def digest(self, digest):
        self.__digest = digest

    @property
    def user_id(self):
        return self.__user_id
    
    @user_id.setter
    def user_id(self, user_id):
        self.__user_id = user_id

    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def url(self):
        return self.__url
    
    @url.setter
    def url(self, url):
        self.__url = url

    @property
    def bucketname(self):
        return self.__bucketname
    
    @bucketname.setter
    def bucketname(self, bucketname):
        self.__bucketname = bucketname

    @property
    def s3credentials(self):
        return self.__s3credentials
    
    @s3credentials.setter
    def s3credentials(self, s3credentials):
        self.__s3credentials = s3credentials

    @property
    def protocol(self):
        return self.__protocol
    
    @protocol.setter
    def protocol(self, protocol):
        self.__protocol = protocol

    @property
    def username(self):
        return self.__username
    
    @username.setter
    def username(self, username):
        self.__username = username

    @property
    def password(self):
        return self.__password
    
    @password.setter
    def password(self, password):
        self.__password = password

    @property
    def hostname(self):
        return self.__hostname
    
    @hostname.setter
    def hostname(self, hostname):
        self.__hostname = hostname

    @property
    def port(self):
        return self.__port
    
    @port.setter
    def port(self, port):
        self.__port = int(port)

    def isF1Credential(self):
        '''The NamedCredential is not subclassed. Clients use this to validate whether
        the credential is for an F1 endpoint.

        Returns
        -------
        :type bool: True if fields are set for F1 credential, False otherwise.
        '''
        if self.username is None:
            return False
        if self.bucketname is not None:
            return False
        return True

    def isS3Credential(self):
        '''The NamedCredential is not subclassed. Clients use this to validate whether
        the credential is for a S3 (bucket) endpoint.

        Returns
        -------
        :type bool: True if fields are set for S3 credential, False otherwise.
        '''
        if self.username is not None:
            return False
        if self.bucketname is None:
            return False
        return True

