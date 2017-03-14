#
# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
class S3Credentials(object): 
    '''
    Provides access to the credentials for accessing simple storage services.
    '''
    def __init__(self, access_key_id=None, secret_key=None):
        self.__access_key_id = access_key_id
        self.__secret_key = secret_key
        
    @property
    def access_key_id(self):
        return self.__access_key_id
    
    @access_key_id.setter
    def access_key_id(self, a_name):
        self.__access_key_id = a_name
        
    @property
    def secret_key(self):
        return self.__secret_key
    
    @secret_key.setter
    def secret_key(self, a_secret_key):
        self.__secret_key = a_secret_key
