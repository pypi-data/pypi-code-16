import requests

from sulfur.response import HTTPResponse
from sulfur.urlcheckerclient import URLCheckerClientMixin


class Client(URLCheckerClientMixin):
    """
    A client to an HTTP server.

    Get contents using the .get() .post(), .delete(), etc methods.
    """

    DEFAULT_CONCRETE_CLASS = None

    def __new__(cls, **kwargs):
        if cls is Client:
            cls = get_server_class()
        new = object.__new__(cls)
        new.__init__(**kwargs)
        return new

    def __init__(self, base_url=None):
        self.base_url = base_url

    def url_normalize(self, url):
        """
        Normalize any given url.

        It can be overriden in subclasses. The default implementation simply
        prepend the home_url to the given url, if not given.
        """

        return (self.base_url or '') + url

    def get(self, url, data=None, **kwargs):
        """
        Opens url using GET.

        Return a Page() instance.
        """

        return self.open(url, 'GET', data, **kwargs)

    def post(self, url, data=None, **kwargs):
        """
        Opens url using POST.

        Return a Response() instance.
        """

        return self.open(url, 'POST', data, **kwargs)

    def put(self, url, data=None, **kwargs):
        """
        Opens url using PUT.

        Return a Response() instance.
        """

        return self.open(url, 'PUT', data, **kwargs)

    def delete(self, url, data=None, **kwargs):
        """
        Opens url using DELETE.

        Return a Response() instance.
        """

        return self.open(url, 'DELETE', data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        """
        Opens url using PATCH.

        Return a Response() instance.
        """

        return self.open(url, 'PATCH', data, **kwargs)

    def open(self, url, verb='GET', data=None, **kwargs):
        """
        Opens url using the given http verb.

        Args:
            url: a valid url
            verb: an HTTP verb (GET, POST, PUT, DELETE, PATCH)
            data: a dictionary of data

        Returns:
            A :cls:`Response` object.
        """

        raise NotImplementedError

    def check_verb(self, verb):
        """
        Raises a ValueError if the given HTTP verb is invalid.
        """

        if verb.upper() not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
            raise ValueError('invalid HTTP verb: %s' % verb)


class HTTPClient(Client):
    """
    Client interface that performs real HTTP requests.

    It uses the requests library to
    """

    def open(self, url, verb, data=None):
        self.check_verb(verb)
        url = self.url_normalize(url)
        method = getattr(requests, verb.lower())
        response = method(url, data)
        return HTTPResponse(response)


class DjangoClient(Client):
    """
    Django-based interface.
    """

    def __init__(self, base_url=None):
        super().__init__(base_url=None)

        from django.test import Client
        self._client = Client()

    def open(self, url, verb, data=None):
        self.check_verb(verb)
        url = self.url_normalize(url)
        method = getattr(self._client, verb.lower())
        return method(url, data)


def get_server_class():
    """
    Return the default global _client class.
    """

    return Client.DEFAULT_CONCRETE_CLASS


def set_server_class(cls):
    """
    Sets the global default _client class.
    """

    Client.DEFAULT_CONCRETE_CLASS = cls


set_server_class(HTTPClient)
