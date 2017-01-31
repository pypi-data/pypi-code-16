"""
Will make request to provided url with given method
and return the response code.

:param url: The URL to test.
:param method: Request method (GET, PUT, POST, etc.)
:param reformat_url: Use the URL as passed or fix/reformat it.
:return: Status code of returned response

EXAMPLE:
>>> from urlcheck import get_response_code as grc
>>> grc('http://arstechnica.com/not_real', method='put')
404
>>> grc('www.yahoo.com/sports')
200
>>> grc('google.com')
200
"""

from requests import request

__version__ = "1.0.0"


def format_url(url: str = None) -> str:
    """
    Take url which may or may-not be formatted and return a formatted one.

    :param url: URL to format.
    :return: Formatted URL.

    EXAMPLE:
    >>> from urlcheck import format_url
    >>> format_url('http://yahoo.com')
    'http://www.yahoo.com'
    >>> format_url('yahoo.com')
    'http://www.yahoo.com'
    >>> format_url('www.yahoo.com')
    'http://www.yahoo.com'
    >>> format_url('http://www.yahoo.com')
    'http://www.yahoo.com'
    """

    if url.startswith('http://www.'):
        formatted = str(url)
    elif url.startswith('www.'):
        formatted = 'http://' + url
    elif url.startswith('http://'):
        formatted = url.replace('//', '//www.')
    else:
        formatted = 'http://www.' + url

    return formatted


def get_response_code(url: str = None,
                      method: str = 'GET',
                      reformat_url: bool = True) -> int:
    """
    Will make request to provided url with given method
    and return the response code.

    :param url: The URL to test.
    :param method: Request method (GET, PUT, POST, etc.)
    :param reformat_url: Use the URL as passed or fix/reformat it.
    :return: Status code of returned response

    EXAMPLE:
    >>> from urlcheck import get_response_code as grc
    >>> grc('http://arstechnica.com/not_real', method='put')
    404
    >>> grc('www.yahoo.com/sports')
    200
    >>> grc('google.com')
    200
    """

    url = format_url(url) if reformat_url else url
    return request(method=method, url=url).status_code
