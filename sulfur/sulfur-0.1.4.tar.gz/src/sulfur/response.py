from lazyutils import lazy, delegate_to


class Response:
    """
    Base class for all responses.

    Attributes:
        content (bytes):
            A raw byte-string with the response data.
        data (str):
            Content as a decoded string.
        status_code:
            Numeric HTTP status code (e.g., 200, 404, etc)
        encoding (str):
            Data encoding
        url (str):
            Request absolute URL
        header (dict):
            A dictionary-like object with the HTTP headers.
    """

    @lazy
    def data(self):
        return self.content.decode(self.encoding)

    content = delegate_to('_data')
    status_code = delegate_to('_data')
    encoding = delegate_to('_data')
    url = delegate_to('_data')
    header = delegate_to('_data')


class HTTPResponse(Response):
    """
    Represents a response to an HTTP request.
    """

    def __init__(self, data):
        self._data = data
