from fdscli.model.common.s3credentials import S3Credentials

class Repository(object): 
    '''A storage endpoint.

    IS-A bucket or IS-A domain (identified by the primary OM service locator).

    Attributes
    ----------
    __uuid (str) : Unique identifier for the endpoint
    __credentials (S3Credentials) : Access key and secret key for S3 endpoint
    __remote_om (str) : URL like 'http://remoteOmUser:remoteOmPasswd@remoteOmHost:remoteOmPort'
    __volume_id (long) : TODO: Likely not needed in CLI abstraction, used on Java side only

    __url (str) : S3 endpoint or Xdi endpoint
    __bucket_name (str) : For S3 endpoint, name of an existing bucket
    __obj_prefix_key (str) : Object prefix key for exported volume in existing bucket
    __new_volume_name (str) : New volume name for import from existing bucket
    __remote_volume_name (str) : For remote clone, the remote volume name
    '''
    def __init__(self, uuid=-1, credentials=None,
        remote_om=None, volume_id=-1, url=None, bucket_name=None, obj_prefix_key=None,
        new_volume_name=None,
        remote_volume_name=None):

        self.__uuid = uuid
        self.__credentials = credentials
        if self.__credentials is None:
            self.__credentials = S3Credentials()
        self.__volume_id = volume_id
        self.__url = url
        self.__bucket_name = bucket_name
        self.__obj_prefix_key = obj_prefix_key
        self.__new_volume_name = new_volume_name
        # Mutually exclusive with bucket name
        self.__remote_om = remote_om
        self.__remote_volume_name = remote_volume_name
        
    @property
    def uuid(self):
        return self.__uuid
    
    @uuid.setter
    def uuid(self, uuid):
        self.__uuid = uuid

    @property
    def credentials(self):
        return self.__credentials

    @credentials.setter
    def credentials(self, credentials):
        self.__credentials = credentials

    @property
    def remote_om(self):
        return self.__remote_om

    @remote_om.setter
    def remote_om(self, remote_om):
        self.__remote_om = remote_om

    @property
    def volume_id(self):
        return self.__volume_id
    
    @volume_id.setter
    def volume_id(self, volume_id):
        self.__volume_id = long(volume_id)

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url

    @property
    def bucket_name(self):
        return self.__bucket_name

    @bucket_name.setter
    def bucket_name(self, bucket_name):
        self.__bucket_name = bucket_name

    @property
    def obj_prefix_key(self):
        return self.__obj_prefix_key

    @obj_prefix_key.setter
    def obj_prefix_key(self, obj_prefix_key):
        self.__obj_prefix_key = obj_prefix_key

    @property
    def new_volume_name(self):
        return self.__new_volume_name

    @new_volume_name.setter
    def new_volume_name(self, new_volume_name):
        self.__new_volume_name = new_volume_name

    @property
    def remote_volume_name(self):
        return self.__remote_volume_name

    @remote_volume_name.setter
    def remote_volume_name(self, remote_volume_name):
        self.__remote_volume_name = remote_volume_name

