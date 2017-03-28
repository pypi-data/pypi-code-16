"""
OpenERP wrapper that use clientlib
"""

from googleapiclient.discovery import build
import logging

from .config import config
from .credentials import get_service_credentials, get_oauth_credentials


class Client(object):
    """Simple wrapper that use clientlib."""

    def __init__(self, endpoint=None, using=None,
                 # Related to service account
                 service_account_key=None,
                 # Related to oauth
                 client_id=None, client_secret=None, refresh_token=None,
                 # General
                 scopes=[],
                 config_file=None, logger=None):
        """
        Creates a new Client.

        If any of ``endpoint``, ``using``, ``service_account_key``,
        this client will attempt to locate from them from environment,
        ~/.google.conf, $HOME/.google.conf /etc/google.conf.
        """
        # Init Logger
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        # Load a custom config file if requested
        if config_file is not None:
            config.read(config_file)

        # Load endpoint
        if endpoint is None:
            endpoint = config.get('default', 'endpoint')

        # Load using
        if using is None:
            using = config.get(endpoint, 'using')

        valid_using = ['service', 'oauth']
        if using not in valid_using:
            raise Exception('using must be one of the following ' +
                            '{0}'.format(valid_using))

        # Related to service account
        if using == 'service':
            if service_account_key is None:
                service_account_key = config.get(endpoint,
                                                 'service_account_key')

        # Related to oauth
        if using == 'oauth':
            if client_id is None:
                client_id = config.get(endpoint, 'client_id')
            if client_secret is None:
                client_secret = config.get(endpoint, 'client_secret')
            if refresh_token is None:
                refresh_token = config.get(endpoint, 'refresh_token')

        # Save scopes
        self.scopes = scopes

        if using == 'service':
            self.credentials = get_service_credentials(service_account_key,
                                                       scopes=scopes)

        elif using == 'oauth':
            self.credentials = get_oauth_credentials(client_id,
                                                     client_secret,
                                                     refresh_token)

    def create_delegated(self, email):
        """Impersonate user."""
        return self.credentials.create_delegated(email)

    def get_directory_client(self, email):
        """Get an admin SDK directory API client."""
        credentials = self.create_delegated(email)
        return build('admin', 'directory_v1', credentials=credentials,
                     cache_discovery=False)

    def get_gmail_client(self):
        """Get a gmail API client."""
        return build('gmail', 'v1', credentials=self.credentials,
                     cache_discovery=False)

