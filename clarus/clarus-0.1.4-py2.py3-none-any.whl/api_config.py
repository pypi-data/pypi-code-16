import clarus.output_types
import logging

logger = logging.getLogger(__name__)

class ApiConfig(object):
    default_output_type = clarus.output_types.CSV
    base_url = 'http://dev.api.clarusft.com/rest/v1/'
    resource_path = 'c:/clarusft/data/test/'            # where to look for data files
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
        pass
    
    def read_secret(self):
        logger.debug('reading API Secret')
        pass
ApiConfig = ApiConfig()