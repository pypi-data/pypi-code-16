import json
import urllib
import urlparse

import requests
from behave_logger import get_logger
from enum import Enum
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

_logger = get_logger(__name__)


class RESTOperation(Enum):
    def __str__(self):
        return self.value

    @property
    def value(self):
        return self._name_

    GET, POST, PUT, DELETE, PATCH, OPTIONS = range(6)


def send_request(rest_operation, url, headers=None, payload=None, **kwargs):
    """
    Sends a REST request of any kind

    :param rest_operation: The :class:`RestOperation` Enum
    :param url: A string representing the resource's URL
    :param headers: (optional) A JSON representation of the headers
    :param payload: (optional) A JSON representation of the payload
    :returns: The response object
    """

    _logger.info(u'Sending {} request to {}'.format(rest_operation.value, url))

    if headers is not None:
        if isinstance(headers, basestring):
            headers = json.loads(headers)
        _logger.info('Headers: {}'.format(headers))

    if payload is not None:
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        _logger.info(u'Payload: {}'.format(payload))

    response = requests.request(rest_operation.value, url, headers=headers, data=payload, **kwargs)

    _logger.info('REST operation finished with status code {}: '
                 '{}'.format(str(response.status_code), response.reason))

    return response


def add_url_query_parameters(url, query_params):
    """
    Adds query parameters to a URL

    :param url: A string representing the URL to add the parameters to
    :param query_params: A JSON dict representing the query parameters as key: value
    :return: A string representing the new URL with the added query parameters
    """
    (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
    url_query_params = urlparse.parse_qsl(query, keep_blank_values=True)

    for key in query_params:
        url_query_params.append((key, query_params[key]))

    return urlparse.urlunparse((scheme, netloc, path, params,
                                urllib.urlencode(url_query_params), fragment))
