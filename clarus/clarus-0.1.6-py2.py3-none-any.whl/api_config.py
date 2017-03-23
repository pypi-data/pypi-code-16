import clarus.output_types
import logging
import os

logger = logging.getLogger(__name__)

class ApiConfig(object):
    default_output_type = clarus.output_types.CSV
    base_url = 'http://dev.api.clarusft.com/rest/v1/'
    resource_path = 'c:/clarusft/data/test/'            # where to look for data files
    key_path      = 'c:/clarusft/keys/'  
    key_file      = 'API-Key.txt'
    secret_file   = 'API-Secret.txt'

    _api_key = None
    _api_secret = None
    
    _key_init = False
    _secret_init = False
        
    def __init__(self):
        pass

    @property
    def api_key(self):
        if (self._api_key is None and self._key_init == False):
            self.read_key()
            self._key_init = True
        return self._api_key
    
    @api_key.setter
    def api_key(self, k):
        self._api_key = k
        
    @property
    def api_secret(self):
        if (self._api_secret is None and self._secret_init == False):
            self.read_secret()
            self._secret_init = True
        return self._api_secret
    
    @api_secret.setter
    def api_secret(self, s):
        self._api_secret = s
        
    def read_key(self):
        logger.debug('reading API Key')
        
        self._api_key = self.read_key_file(self.key_file)
        if (self._api_key is None):
            if 'CHARM_API_KEY' in os.environ:
                self._api_key = os.environ['CHARM_API_KEY']
        
        logger.debug('API key set to {}'.format(self._api_key))
    
    def read_secret(self):
        logger.debug('reading API Secret')
        
        self._api_secret = self.read_key_file(self.secret_file)
        if (self._api_secret is None):
            if 'CHARM_API_SECRET' in os.environ:
                self._api_secret = os.environ['CHARM_API_SECRET']
        
        if (self._api_secret is not None and len(self._api_secret) > 40):
            self._api_secret = self.kms_decrypt(self._api_secret)
    
    def read_key_file(self, file):
        if (os.path.isfile(file)) :
            key = open(file).read()
        elif os.path.isdir(self.key_path):
            key = open(self.key_path+file).read()
        else:
            key = None
        return key
    
    def kms_decrypt(self, ciphertext):
        try:
            import boto3
            from base64 import b64decode 
            plaintext = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ciphertext))['Plaintext']
            return plaintext
        except:
            logger.exception('Error decrypting ciphertext')
            return ciphertext
    
ApiConfig = ApiConfig()