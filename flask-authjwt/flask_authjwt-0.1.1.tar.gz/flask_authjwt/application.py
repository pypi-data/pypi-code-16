import jwt
import logging
import os
import json
from datetime import datetime, timedelta
from helpers import get_payload_from_token, get_configuration
from helpers import verify_header, execute_basic_authentication, execute_bearer_authentication
from flask import request
from flask_restful import Resource, abort
from models import BasicAuth


def authenticate_client(client):
    """Decorator to verify requests from web clients."""
    def func(origin):
        """Inner."""
        def inner(self, *args, **kwargs):
            """Inner."""
            headers = request.headers
            settings = get_configuration()
            logging.warning(settings)
            if settings:
                kind, token = verify_header(headers, settings)

                if 'Basic' in kind:
                    if execute_basic_authentication(token, BasicAuth):
                        return origin(self, *args, **kwargs)
                    else:
                        logging.warning("Error verifying Basic Client")
                        abort(403, message='Unauthorized')
                elif 'Bearer' in kind:
                    if execute_bearer_authentication(self, kind, token, settings, client, headers):
                        return origin(self, *args, **kwargs)
                    else:
                        logging.warning("Error verifying Bearer Client")
                        abort(403, message='Unauthorized')
            else:
                logging.warning("jwt settings file is not configured")
                abort(403, message='Unauthorized')

        inner.__name__ = origin.__name__
        inner.__doc__ = origin.__doc__
        inner.__dict__.update(origin.__dict__)
        return inner
    return func
