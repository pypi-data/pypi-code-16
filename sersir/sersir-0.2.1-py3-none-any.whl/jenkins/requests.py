"""Extract information from the jenkins api"""
import json
import warnings
import urllib.parse
import urllib.request

import logging

logger = logging.getLogger(__name__)


class PreemptiveBasicAuthHandler(urllib.request.HTTPBasicAuthHandler):
    """Always send a basic authentication header instead of waiting a 4** status code reply"""

    def http_request(self, req):
        """Extend the http"""
        url = req.get_full_url()
        realm = None
        user, password = self.passwd.find_user_password(realm, url)
        if password:
            import base64
            raw = "%s:%s" % (user, password)
            auth = "Basic " + base64.b64encode(raw.encode()).decode("ascii")
            req.add_unredirected_header(self.auth_header, auth)
        return req

    https_request = http_request


def jobs_status(host=None, user=None, token=None, path='/', scheme='https', insecure=False):
    """Issue http request against the jenkins api"""
    if host is None or user is None or token is None:
        raise AttributeError('host, user or token is None and this an invalid call')

    if scheme != 'http' and scheme != 'https':
        raise AttributeError('Unknown scheme "{scheme}". Only http and https are supported!'.format(scheme=scheme))

    if scheme == 'http':
        if not insecure:
            raise RuntimeError('Tried to use insecure scheme. Please adjust the explicit parameter "insecure".')
        else:
            warnings.warn(RuntimeWarning('Try to access api via insecure scheme. Do this only on a test system!'))

    logger.debug(
        'Called jobs_status(host=%s, user=%s, token=%s, path=%s, scheme=%s)',
        host, user, token, path, scheme
    )

    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    top_level_url = scheme + '://' + host + path
    password_mgr.add_password(None, top_level_url, user, token)

    # Create opener on top of handler on top of the password manager
    handler = PreemptiveBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)

    # Install our opener as the default one
    urllib.request.install_opener(opener)

    # Retrieve the current state from the api
    params = {
        'tree': 'jobs[name,color]'
    }

    url_parts = (
        scheme,  # Scheme
        host,  # netloc
        path + 'api/json',  # path
        urllib.parse.urlencode(params),  # query
        ''  # fragment
    )

    response_content = read_url(url_parts)

    # Decode byte stream into utf-8 string
    response_content_decoded = response_content.decode('utf-8')
    # Parse json string
    data = json.loads(response_content_decoded)
    logger.debug('Gathered jobs from the jenkins host.')

    return data['jobs']


def read_url(url_parts):
    """Wrap the actual execution of the request"""
    logger.debug('Gather jobs from the jenkins host.')
    response = urllib.request.urlopen(urllib.parse.urlunsplit(url_parts))
    # Read bytestream into variable
    return response.read()
