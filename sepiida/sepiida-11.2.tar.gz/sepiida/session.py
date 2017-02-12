import logging

import requests
from flask import current_app, g, request, session
from flask_httpauth import HTTPBasicAuth

from sepiida.errors import APIException, AuthenticationException, Error

auth = HTTPBasicAuth()
LOGGER = logging.getLogger(__name__)

def register_session_handlers(app, pao_root, whitelist=None, internal_domains=None):
    app.config['SEPIIDA_PAO_ROOT'] = pao_root
    app.config['SEPIIDA_INTERNAL_DOMAINS'] = app.config.get('SEPIIDA_INTERNAL_DOMAINS', []) + list(internal_domains or [])

    app.before_request(require_user)
    whitelist = whitelist or []
    for endpoint in whitelist:
        public_endpoint(app, endpoint)

    app.config['PUBLIC_ENDPOINTS'] = app.config.get('PUBLIC_ENDPOINTS', []) + whitelist

    @auth.verify_password
    def verify_password(username, password): # pylint: disable=unused-variable
        if username == 'api' and password == current_app.config.get('API_TOKEN', None):
            return True
        else:
            url = '{}/sessions/'.format(pao_root)
            response = requests.get(url, auth=(username, password))
            if not response.status_code == 200:
                return False
            g.current_user = response.json()
            return True


def current_user_uri():
    try:
        return g.current_user.get('uri', None)
    except AttributeError:
        return None

def current_user():
    if g.endpoint_authenticated:
        return g.current_user

    if 'uri' not in g.current_user:
        return

    if 'uuid' in g.current_user:
        return g.current_user

    url = '{}/sessions/'.format(current_app.config['SEPIIDA_PAO_ROOT'])
    cookies = { 'session': request.cookies.get('session', None) }
    response = requests.get(url, cookies=cookies)
    if not response.status_code == 200:
        raise AuthenticationException(
                status_code=400,
                error_code='retrieving-user-details-error',
                title="An error occured while retrieving the user details.")
    g.current_user = response.json()
    return g.current_user


def is_whitelisted(endpoint, method):
    blueprint, _, basename = endpoint.rpartition('.')
    basename = basename or blueprint

    endpoint_with_method = '{}.{}'.format(endpoint, method.lower())
    defaults = request.url_rule.defaults
    if defaults and not defaults.get('_single_resource', False) and method == "GET":
        endpoint_with_method = '{}.list'.format(endpoint)

    public_endpoints = current_app.config['PUBLIC_ENDPOINTS']
    return any([
        basename             in public_endpoints,
        endpoint             in public_endpoints,
        endpoint_with_method in public_endpoints,
    ])


def public_endpoint(app, f):
    try:
        endpoint_name = f.__name__
    except AttributeError:
        endpoint_name = f
    app.config['PUBLIC_ENDPOINTS'] = app.config.get('PUBLIC_ENDPOINTS', []) + [endpoint_name]

def get_endpoint_authentication():
    resource = getattr(current_app, 'endpoints', {}).get(request.endpoint, None)
    if resource:
        try:
            return resource.authenticate()
        except Error as e:
            raise APIException(errors=[e])

def require_user():
    # pylint: disable=too-many-branches
    g.current_user = {}
    g.endpoint_authenticated = False
    if 'Access-Control-Request-Method' in request.headers and request.method == 'OPTIONS':
        return

    elif not request.endpoint:
        return

    elif request.path.startswith(current_app.static_url_path):
        return

    elif is_whitelisted(request.endpoint, request.method):
        return

    endpoint_authentication = get_endpoint_authentication()
    if endpoint_authentication:
        g.current_user = endpoint_authentication
        g.endpoint_authenticated = True
    elif request.authorization:
        if auth.authenticate(request.authorization, request.authorization.password):
            return
        else:
            raise AuthenticationException(
                    status_code=403,
                    error_code='invalid-credentials',
                    title='The API key and secret you provided were not recognized')

    elif 'session' not in request.cookies and 'Authorization' not in request.headers:
        raise AuthenticationException(
                status_code=403,
                error_code='no-credentials-provided',
                title="You must include a valid session cookie or an API token and secret "
                    "encoded in your Authorization header according to Basic Auth standards (RFC 2617)")

    elif 'Authorization' in request.headers:
        raise AuthenticationException(
                status_code=400,
                error_code='not-well-formed-authorization-header',
                title="The authorization header you have provided was not properly formatted. "
                    "Please see RFC 2617")

    elif len(session) == 0:
        raise AuthenticationException(
                status_code=403,
                error_code='empty-session-provided',
                title="The session cookie you have provided does not contain any data")

    elif 'user_uri' not in session:
        raise AuthenticationException(
                status_code=403,
                error_code='invalid-session-provided',
                title="The session cookie you have provided does not contain valid data")

    elif 'user_uri' in session:
        g.current_user['uri'] = session['user_uri']

        if not g.current_user['uri']:
            raise AuthenticationException(
                    status_code=400,
                    error_code='unkown-user-error',
                    title="The user information you have provided is not valid or does not exist.")

    else:
        raise AuthenticationException(
                status_code=403,
                error_code='unkown-authentication-error',
                title="Not sure what happened, but authentication failed. Tell Authentise")

def is_api_user():
    if request.authorization:
        password = auth.get_password_callback(request.authorization.username)
        return auth.authenticate(request.authorization, password)
    else:
        return False

def is_internal_user():
    return bool(request.authorization) and \
           request.authorization.username == 'api' and \
           request.authorization.password == current_app.config.get('API_TOKEN')
