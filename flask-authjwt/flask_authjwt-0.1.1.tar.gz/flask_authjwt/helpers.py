"""Helpers."""
import json
import logging
import base64
from caching import cache
from flask_restful import Resource, abort
from authentication_types import BasicAuthentication
from authentication_types import JWTAuthentication
CONFIG_FILE_PATH = 'auth_jwt_settings.json'


def get_payload_from_token(token):
    """get_payload_from_token."""
    # JWT is in three parts, header, token, and signature
    # separated by '.'.
    try:
        token_parts = token.split('.')
        encoded_token = token_parts[1]

        # Base64 strings should have a length divisible by 4.
        # If this one doesn't, add the '=' padding to fix it.
        leftovers = len(encoded_token) % 4
        if leftovers == 2:
            encoded_token += '=='
        elif leftovers == 3:
            encoded_token += '='

        # URL-safe base64 decode the token parts.
        decoded = base64.urlsafe_b64decode(
            encoded_token.encode('utf-8')).decode('utf-8')

        #  Load decoded token into a JSON object.
        jwt = json.loads(decoded)

        return jwt
    except Exception, e:
        logging.error(e)
        return False


@cache('jwt_configuration_file', ttl=3600)
def get_configuration():
    """Get configuration from configuration file."""
    try:
        with open(CONFIG_FILE_PATH) as data_file:
            settings = json.load(data_file)
            data_file.close()
            return settings
    except Exception, e:
        logging.error(e)
        return False


def verify_header(headers, settings):
    """Verify if authorization header is valid."""
    authorization = headers.get('Authorization')

    if authorization:
        splited_token = authorization.split(' ')
        if len(splited_token) == 2:
            kind = splited_token[0]
            token = splited_token[1]
            kind_valid = settings.get(kind)
            if kind_valid:
                return kind, token
            else:
                logging.warning('Unsupported kind of authentication')
                abort(403, message='Unauthorized')
        else:
            logging.warning('Invalid Authorization header')
            abort(403, message='Invalid header')
    else:
        logging.warning('Authorization header was not found')
        abort(403, message='Unauthorized')


def execute_basic_authentication(token, client):
    """Execute basic authentication process."""
    basic_auth = BasicAuthentication()
    return basic_auth.verify(token, client)


def execute_bearer_authentication(self, kind, token, settings, client_model, headers):
    """Execute bearer jwt authentication process."""
    bearer_settings = settings.get("Bearer")

    # Checks if settings are correct
    if not bearer_settings:
        logging.warning("Bearer not defined on settings")
        return False
    client_settings = bearer_settings.get('ClientApp')
    if not client_settings:
        logging.warning("ClientApp not defined on client_settings")
        return False
    client_fields = client_settings.get('Fields')
    if not client_fields:
        logging.warning("Fields not defined on clientApp_settings")
        return False

    payload = get_payload_from_token(token)
    if not payload:
        logging.warning("Couldn't get payload from JWT token")
        return False

    # Gets client id_from payload
    client_id_from_payload = get_client_attribute_from_payload(payload, "ClientId", client_fields)
    user_from_payload = payload.get("user")
    if user_from_payload:
        setattr(self, "user", user_from_payload)

    if not client_id_from_payload:
        logging.warning("Couldn't get client id from payload")
        return False
    # Gets client secret from payload
    secret = client_fields.get("Secret")
    if not secret:
        logging.warning("Couldn't get client secret from settings")
        return False
    # GET OBJECT DATA FROM APP ENGINE
    client_obj = client_model.query(getattr(client_model, client_fields.get('ClientId')) == client_id_from_payload).get()
    if not client_obj:
        logging.warning("Couldn't get client data from app engine")
        return False

    verify_expiration = client_fields.get("VerifyExpiration")
    verify_signature = client_fields.get("VerifySignature")
    jwt_auth = JWTAuthentication()
    if verify_expiration:
        jwt_auth.verify_expiration = getattr(client_obj, verify_expiration, False)
    if verify_signature:
        jwt_auth.verify_signature = getattr(client_obj, verify_signature, True)

    decoded_token = jwt_auth.decodeAndVerify(token, getattr(client_obj, secret))
    if (not decoded_token):
        logging.warning("Invalid token received, couldn't decode")
        return False
    if ('Origin' not in headers):
        logging.warning("Couldn't obtain host, unknown host")
        return False
    urls_white_list = getattr(client_obj, client_fields.get('UrlsWhiteList'))
    if (not urls_white_list):
        logging.warning("Forbbiden: client does not have configured origin hosts")
        return False
    if (headers.get('Origin') not in urls_white_list):
        logging.warning('Forbbiden: origin is not allowed')
        return False
    setattr(self, 'client', client_obj)
    return True


def get_client_attribute_from_payload(payload, attribute, client_fields):
    """Decode jwt token payload."""
    exist_attribute = client_fields.get(attribute)
    if not exist_attribute:
        logging.warning("Attribute doesn't exist")
        return None
    return payload.get(exist_attribute)
