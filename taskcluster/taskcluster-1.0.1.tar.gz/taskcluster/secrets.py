# coding=utf-8
#####################################################
# THIS FILE IS AUTOMATICALLY GENERATED. DO NOT EDIT #
#####################################################
# noqa: E128,E201
from .client import BaseClient
from .client import createApiClient
from .client import config
from .client import createTemporaryCredentials
from .client import createSession
_defaultConfig = config


class Secrets(BaseClient):
    """
    The secrets service provides a simple key/value store for small bits of secret
    data.  Access is limited by scopes, so values can be considered secret from
    those who do not have the relevant scopes.

    Secrets also have an expiration date, and once a secret has expired it can no
    longer be read.  This is useful for short-term secrets such as a temporary
    service credential or a one-time signing key.
    """

    classOptions = {
        "baseUrl": "https://secrets.taskcluster.net/v1"
    }

    def set(self, *args, **kwargs):
        """
        Set Secret

        Set the secret associated with some key.  If the secret already exists, it is
        updated instead.

        This method takes input: ``http://schemas.taskcluster.net/secrets/v1/secret.json#``

        This method is ``stable``
        """

        return self._makeApiCall(self.funcinfo["set"], *args, **kwargs)

    def remove(self, *args, **kwargs):
        """
        Delete Secret

        Delete the secret associated with some key.

        This method is ``stable``
        """

        return self._makeApiCall(self.funcinfo["remove"], *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Read Secret

        Read the secret associated with some key.  If the secret has recently
        expired, the response code 410 is returned.  If the caller lacks the
        scope necessary to get the secret, the call will fail with a 403 code
        regardless of whether the secret exists.

        This method takes output: ``http://schemas.taskcluster.net/secrets/v1/secret.json#``

        This method is ``stable``
        """

        return self._makeApiCall(self.funcinfo["get"], *args, **kwargs)

    def list(self, *args, **kwargs):
        """
        List Secrets

        List the names of all secrets that you would have access to read. In
        other words, secret name `<X>` will only be returned if a) a secret
        with name `<X>` exists, and b) you posses the scope `secrets:get:<X>`.

        This method takes output: ``http://schemas.taskcluster.net/secrets/v1/secret-list.json#``

        This method is ``stable``
        """

        return self._makeApiCall(self.funcinfo["list"], *args, **kwargs)

    def ping(self, *args, **kwargs):
        """
        Ping Server

        Respond without doing anything.
        This endpoint is used to check that the service is up.

        This method is ``stable``
        """

        return self._makeApiCall(self.funcinfo["ping"], *args, **kwargs)

    funcinfo = {
        "get": {           'args': ['name'],
            'method': 'get',
            'name': 'get',
            'output': 'http://schemas.taskcluster.net/secrets/v1/secret.json#',
            'route': '/secret/<name>',
            'stability': 'stable'},
        "remove": {           'args': ['name'],
            'method': 'delete',
            'name': 'remove',
            'route': '/secret/<name>',
            'stability': 'stable'},
        "ping": {           'args': [],
            'method': 'get',
            'name': 'ping',
            'route': '/ping',
            'stability': 'stable'},
        "set": {           'args': ['name'],
            'input': 'http://schemas.taskcluster.net/secrets/v1/secret.json#',
            'method': 'put',
            'name': 'set',
            'route': '/secret/<name>',
            'stability': 'stable'},
        "list": {           'args': [],
            'method': 'get',
            'name': 'list',
            'output': 'http://schemas.taskcluster.net/secrets/v1/secret-list.json#',
            'route': '/secrets',
            'stability': 'stable'},
    }


__all__ = ['createTemporaryCredentials', 'config', '_defaultConfig', 'createApiClient', 'createSession', 'Secrets']
