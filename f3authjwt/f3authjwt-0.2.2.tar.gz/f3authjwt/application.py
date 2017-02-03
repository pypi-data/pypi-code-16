import jwt
import logging
import os
import json
from datetime import datetime, timedelta
from helpers import get_payload_from_token, get_configuration
from helpers import verify_header, execute_basic_authentication, execute_bearer_authentication

from ferris3 import Service
import ferris3 as f3


def authenticate_client(client):
    """Decorator to verify requests from web clients."""
    def func(origin):
        """Inner."""
        def inner(self, *args, **kwargs):
            """Inner."""
            headers = self.request_state._HttpRequestState__headers
            settings = get_configuration()
            kind, token = verify_header(headers, settings)

            if 'Basic' in kind:
                if execute_basic_authentication(kind, token, settings):
                    return origin(self, *args, **kwargs)
                else:
                    logging.warning("Error verifying Basic Client")
                    raise f3.ForbiddenException('Unauthorized')
            elif 'Bearer' in kind:
                if execute_bearer_authentication(self, kind, token, settings, client, headers):
                    return origin(self, *args, **kwargs)
                else:
                    logging.warning("Error verifying Bearer Client")
                    raise f3.ForbiddenException('Unauthorized')
        inner.__name__ = origin.__name__
        inner.__doc__ = origin.__doc__
        inner.__dict__.update(origin.__dict__)
        return inner
    return func
