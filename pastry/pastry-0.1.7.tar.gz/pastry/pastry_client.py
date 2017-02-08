import os
import yaml
import requests

from pastry.utils.auth import signed_headers


class PastryClient(object):
    _server = None
    _organization = None
    _client = None
    _keypath = None
    initialized = False
    verify = True

    @classmethod
    def initialize(cls, server, organization, client, keypath):
        cls._server = server
        cls._organization = organization
        cls._client = client
        cls._keypath = keypath
        cls.initialized = True

    @classmethod
    def load_config(cls, config_path=None):
        if not config_path:
            config_path = os.path.join(
                os.environ['HOME'], '.chef', 'pastry.yaml')
        if not os.path.exists(config_path):
            raise ValueError(
                'PastryClient not initialized and %s does not exist' %
                config_path
            )
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file.read())
        cls.initialize(
            config['server'],
            config['organization'],
            config['client'],
            config['keypath']
        )

    @classmethod
    def get_url(cls, endpoint):
        if not cls.initialized:
            cls.load_config()
        return cls._server, (endpoint % {'org': cls._organization})

    @classmethod
    def call(cls, endpoint, method='GET', data=None):
        server, path = cls.get_url(endpoint)
        headers = signed_headers(
            cls._client, cls._keypath, server, path, method=method, data=data)
        resp = requests.get(
            '%s%s' % (server, path), headers=headers, verify=cls.verify)
        print resp.text
