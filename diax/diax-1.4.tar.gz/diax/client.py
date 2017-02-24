import json
import logging
import os
import requests
import urllib
import yaml

import diax.errors
import diax.uri

LOGGER = logging.getLogger(__name__)

CREDENTIALS_FILE = os.path.join(os.environ['HOME'], '.authentise', 'credentials')
class Client():
    def __init__(self, environment, impersonate=None, internal_token=None, password=None, username=None,):
        self.environment    = environment
        self.impersonate    = impersonate
        self.internal_token = internal_token
        self.password       = password
        self.session        = requests.Session()
        self.username       = username

    def _do_login(self):
        if self.internal_token:
            LOGGER.info("No login necessary, using internal token")
            self.session.auth = ('api', self.internal_token)
            return
        payload = {
            'password'  : self.password,
            'username'  : self.username,
        }
        self.post('users', '/sessions/', payload)

    def _ensure_has_credentials(self):
        if self.username and self.password:
            LOGGER.debug("Using credentials provided via commandline")
            return
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'r') as f:
                data = yaml.load(f)
            credentials = data.get(self.environment)
            if not credentials:
                raise diax.errors.CredentialsError("You have a {} file but it needs a section for environment {}".format(CREDENTIALS_FILE, self.environment))
            self.password = credentials.get('password')
            self.username = credentials.get('username')
            if not self.username:
                raise diax.errors.CredentialsError("You have a section in {} for environment {} but it doesn't have a username".format(CREDENTIALS_FILE, self.environment))
            if not self.password:
                raise diax.errors.CredentialsError("You have a section in {} for environment {} but it doesn't have a password".format(CREDENTIALS_FILE, self.environment))
            return
        raise diax.errors.CredentialsError("You need to either specify credentials on the commandline with -u and -p or you need to create a credentials file at {}".format(CREDENTIALS_FILE))

    def _get_user_uri(self, username):
        results = self.list('users', '/users/', filters={'username': username})
        if results:
            return results[0]['uri']

    def _maybe_impersonate(self):
        if not self.impersonate:
            return
        LOGGER.debug("Impersonating %s", self.impersonate)
        uri = self.impersonate if diax.uri.is_uri(self.impersonate, 'users', '/users/') else self._get_user_uri(self.impersonate)
        if not uri:
            raise diax.errors.ImpersonationError("The value '{}' is not a user URI or username".format(self.impersonate))
        payload = {
            'impersonating' : uri,
        }
        self.put('users', '/sessions/0/', payload)

    def _validate(self, response, method, url):
        if not response.ok:
            raise diax.errors.RequestError(method, url, response)
        if response.status_code == 204 or response.status_code == 201:
            return None, response.headers
        try:
            return response.json(), response.headers
        except ValueError:
            return response.text, response.headers

    def get(self, service, path, filters={}):
        url = self.url(service, path, filters)
        response = self.session.get(url)
        out, _ = self._validate(response, 'GET', url)
        return out

    def list(self, service, path, filters={}):
        result = self.get(service, path, filters=filters)
        return result['resources']

    def login(self):
        self._ensure_has_credentials()
        self._do_login()
        self._maybe_impersonate()

    def options(self, service, path):
        url = self.url(service, path)
        response = self.session.options(url)
        out, _ = self._validate(response, 'OPTIONS', url)
        return out

    def post(self, service, path, payload):
        url = self.url(service, path)
        response = self.session.post(url, json=payload)
        out, headers = self._validate(response, 'POST', url)
        return out, headers

    def put(self, service, path, payload):
        url = self.url(service, path)
        response = self.session.put(url, json=payload)
        out, _ = self._validate(response, 'PUT', url)
        return out

    def rawget(self, url):
        return self._validate(self.session.get(url), 'GET', url)

    def url(self, service, path, filters=None):
        _url = "https://{}.{}{}".format(service, self.environment, path)
        queryargs = {}
        filters = filters or {}
        queryargs.update({'filter[{}]'.format(k): v for k, v in filters.items()})
        if queryargs:
            _url += '?' + urllib.parse.urlencode(queryargs)
        return _url

    def streamevents(self):
        _url = self.url('events', '/')
        response = self.session.get(_url, stream=True)
        if not response.ok:
            raise diax.errors.RequestError('GET', _url, response)
        for line in response.iter_lines():
            if line:
                yield json.loads(line)

def create(args):
    "Create a client to talk to 3DIAX with the specified environment"
    return Client(
        environment         = args.environment,
        impersonate         = args.impersonate,
        internal_token      = args.internal_token,
        password            = args.password,
        username            = args.username,
    )

