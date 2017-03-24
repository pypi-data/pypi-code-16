from collections import Mapping
from collections import Sequence

from sulfur.errors import ValidationError


def check_url(url, url_format=None,
              method=None, post=None,
              login=None, login_required=False,
              codes=range(200, 300),
              html5=False, html5_validator=None, xhtml=False,
              client=None,
              follow_links=False,
              raises=True):
    """
    Check if response obey certain constraints.

    Args:
        url (str):
            Page's url. It uses url_format to format the url as
            ``url.format(**url_format)``. If a list of urls is given, it tests
            each url separately. If a dicionary is passed, it should map urls
            to error codes.
        url_format (dict):
            A dictionary used to format url strings.
        method (str):
            HTTP method used to retrieve page. (default: 'GET').
        post (dict):
            A dictionary with post data. If given, makes default method='POST'.
        codes (sequence):
            a list of allowed HTTP response codes.
        login (str or tuple):
            Can be either a username or a tuple with (username, password) used
            to login just before making the request.
        login_required (bool):
            If True, anonymous users must either return a 401, 403, 404 or it
            must be a redirect to a login page. If login is given, it will test
            both if one of these error codes is returned for anonymous users
            and proceeds with the regular evaluation for logged in users.
        html5 (bool):
            If True, makes sure that the response is valid HTML5.
        html5_validator:
            Method used to validate the HTML5 code.
        xhtml (bool):
            If True, makes sure the response is valid XHTML.
        raises (bool):
            If False, return True/False instead of raising an exception.
        client:
            A Client instance for making http requests.
    """

    kwargs = locals()
    kwargs.pop('raises')
    kwargs.pop('url_format')
    kwargs.pop('codes')
    kwargs.pop('url')
    if kwargs.pop('follow_links'):
        raise NotImplementedError('follow_links is not implemented yet!')

    # The worker function has a simplified interface: it always raises a
    # validation error and accept only simple string url arguments.
    try:
        urls = _normalize_url_input(url, url_format, codes)
        for url_item, codes in urls.items():
            _check_url_worker(url_item, codes=codes, **kwargs)
    except ValidationError:
        if raises:
            raise
        return False
    if not raises:
        return True


def _normalize_url_input(url, url_format, codes):
    if isinstance(url, Mapping):
        result = url
    elif isinstance(url, (str, bytes)):
        result = {url: codes}
    elif isinstance(url, Sequence):
        result = {url_item: codes for url_item in url}
    else:
        raise TypeError('invalid url type: %s' % url.__class__.__name__)

    if url_format:
        return {k.format(**url_format): v for k, v in result.items()}
    else:
        return result


def _get_valid_client(client, login):
    from sulfur.client import Client

    client = client or Client()
    if login:
        if isinstance(login, (tuple, list)):
            username, password = login
            client.login(username=username, password=password)
        else:
            client.force_login(login)
    return client


def _check_url_worker(url, method=None, post=None,
                      login=None, login_required=False,
                      codes=None, html5=False, html5_validator=None,
                      xhtml=False, client=None):

    client = _get_valid_client(client, login)

    # Build kwargs for executing client's .get(), .post() or other HTTP methods
    if post and method is None:
        method = 'POST'
    method = method or 'GET'

    # Fetch data from server object
    args = (post,) if post else ()
    response = client.open(url, method, *args)

    # Check response code
    if isinstance(codes, int):
        codes = [codes]
    status_code = response.status_code
    if status_code not in codes:
        msg = '%s: received invalid status code: %s' % (url, status_code)
        raise ValidationError(msg)

    # Now we check if the content HTML data validates
    if html5:
        html5_validator = _get_html5_validator(html5_validator)
        try:
            html5_validator(response.content)
        except ValidationError as ex:
            raise ValidationError('%s: %s' % (url, ex))


def _get_html5_validator(html5_validator):
    """
    Normalize the html5_validator parameter from check_url.
    """

    from sulfur.validators import Html5Validator

    if html5_validator is None:
        html5_validator = 'default'
    if callable(html5_validator):
        return html5_validator
    return Html5Validator.as_validator(html5_validator)


def check_ok(url, **kwargs):
    """
    Like :func:`check_url`, but checks if response code is either in the
    2xx or in the 3xx range.
    """

    return check_url(url, codes=range(200, 400), **kwargs)


def check_2xx(url, **kwargs):
    """
    Like :func:`check_url`, but checks if response code is in the 2xx
    range.
    """

    return check_url(url, codes=range(200, 300), **kwargs)


def check_3xx(url, **kwargs):
    """
    Like :func:`check_url`, but checks if response code is in the 3xx
    range.
    """

    return check_url(url, codes=range(300, 400), **kwargs)


def check_4xx(url, **kwargs):
    """
    Like :func:`check_url`, but checks if response code is in the 4xx
    range.
    """

    return check_url(url, codes=range(400, 500), **kwargs)


def check_404(url, **kwargs):
    """
    Like :func:`check_url`, but checks if response code is 404.
    """

    return check_url(url, codes=[404], **kwargs)


def check_5xx(url, **kwargs):
    """
    Like :func:`check_url`, but checks if response code is in the 5xx
    range.
    """

    return check_url(url, codes=range(500, 600), **kwargs)


# Aliases
def check_success(url, **kwargs):
    """
    Alias to :func:`check_2xx`.
    """
    return check_2xx(url, **kwargs)


def check_redirect(url, **kwargs):
    """
    Alias to :func:`check_3xx`.
    """
    return check_3xx(url, **kwargs)


def check_client_error(url, **kwargs):
    """
    Alias to :func:`check_4xx`.
    """
    return check_4xx(url, **kwargs)


def check_server_error(url, **kwargs):
    """
    Alias to :func:`check_5xx`.
    """
    return check_5xx(url, **kwargs)
