"""
Module for working with the Black Goat API. http://diging.github.io/black-goat.
"""


import time, os, json, requests

GOAT_APP_TOKEN = os.environ.get('GOAT_APP_TOKEN', '')
GOAT = os.environ.get('GOAT', '')
GOAT_MAX_RETRIES = os.environ.get('GOAT_MAX_RETRIES', 50)
GOAT_WAIT_INTERVAL = eval(os.environ.get('GOAT_WAIT_INTERVAL', '0.8'))


class GoatList(list):
    def json(self):
        return json.dumps([o.data for o in self])


class BaseGoatObject(object):
    """
    Base class for all Goat classes.
    """

    def __init__(self, **data):
        self._set_data(data)

    def json(self):
        return json.dumps(self)

    def _set_data(self, data):
        self.data = data
        pk = data.get('id', None)
        self.id = int(pk) if pk else None
        self.identifier = data.get('identifier', None)
        return data

    @classmethod
    def wait(cls):
        time.sleep(GOAT_WAIT_INTERVAL)

    @staticmethod
    def headers():
        return {'Authorization': 'Token %s' % GOAT_APP_TOKEN}

    def _path(self, partial):
        if not partial.endswith('/'):
            partial += u'/'
        if not partial.startswith('/') or not GOAT.endswith('/'):
            partial = u'/' + partial
        return GOAT + partial

    @classmethod
    def _handle_response(cls, response):
        if response.status_code not in [requests.codes.ok, 201]:

            raise IOError('Goat responded with %i' % response.status_code)
        return response.json()

    @property
    def create_endpoint(self):
        return self._path(self.path)

    @property
    def read_endpoint(self):
        return self._path('%s/%i/' % (self.path, self.id))

    @property
    def update_endpoint(self):
        return self._path('%s/%i/' % (self.path, self.id))

    @classmethod
    def list(cls, **params):
        partial = cls.path

        if not partial.endswith('/'):
            partial += u'/'
        if not partial.startswith('/') or not GOAT.endswith('/'):
            partial = u'/' + partial

        path = GOAT + partial
        data = cls._handle_response(requests.get(path, params=params))
        return GoatList([cls(**datum) for datum in data.get('results')])

    def create(self):
        if self.id:
            raise RuntimeError('%s already exists' % type(self).__name__)
        response = requests.post(self.create_endpoint, data=self.data, headers=self.headers())
        return self._set_data(BaseGoatObject._handle_response(response))

    def read(self):
        response = requests.get(self.read_endpoint, headers=self.headers())
        return self._set_data(BaseGoatObject._handle_response(response))

    def update(self):
        if not self.id:
            raise RuntimeError('Must set id to update %s' % type(self).__name__)
        response = requests.post(self.update_endpoint, data=self.data, headers=self.headers())
        return self._set_data(BaseGoatObject._handle_response(response))

    def _update_from_remote(self):
        self.data = self.read()


class Concept(BaseGoatObject):
    path = 'concept'

    @staticmethod
    def retrieve(identifier):
        partial = 'retrieve/'
        if not GOAT.endswith('/'):
            partial = '/' + partial
        response = requests.get(GOAT + partial, params={'identifier': identifier})
        datum = cls._handle_response(response)
        return Concept(**datum)

    @classmethod
    def identical(cls, identifier):
        partial = 'identical/'
        if not GOAT.endswith('/'):
            partial = '/' + partial
        response = requests.get(GOAT + partial, params={'identifier': identifier})
        data = cls._handle_response(response)
        return GoatList([cls(**datum) for datum in data.get('results')])

    @classmethod
    def search(cls, q, **params):
        # Triggers an asynchronous search task across multiple authorities.
        partial = 'search/'
        if not GOAT.endswith('/'):
            partial = '/' + partial
        params.update({'q': q})
        response = requests.get(GOAT + partial, params=params, headers=cls.headers())

        # Check back until the results are ready.
        r = 0
        while response.status_code == 202:
            if r > GOAT_MAX_RETRIES:
                raise IOError('Search failed: max retries exceded')
            # We will be redirected to a search-specific poll URL, so we want
            #  to call the final rather than the original url.
            response = requests.get(response.url, headers=cls.headers())
            cls.wait()
            r += 1

        data = cls._handle_response(response)
        return GoatList([cls(**datum) for datum in data.get('results')])


class Identity(BaseGoatObject):
    path = 'identity'


class IdentitySystem(BaseGoatObject):
    path = 'identitysystem'


class Authority(BaseGoatObject):
    path = 'authority'
