from __future__ import absolute_import, division, print_function, unicode_literals

from configparser import ConfigParser, NoSectionError
from os.path import expanduser, join
import requests

from amaascore.exceptions import AMaaSException


class Interface(object):
    """
    Currently this class doesn't do anything - but I anticipate it will be needed in the future.
    """

    def __init__(self, endpoint, use_auth=False, config_filename=None):
        # Add authentication routine here
        self.config_filename = config_filename
        self.auth_token = self.read_token() if use_auth is True else ''
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update({'Authorization': self.auth_token})

    @staticmethod
    def generate_config_filename():
        home = expanduser("~")
        return join(home, '.amaas.cfg')

    def read_token(self):
        if self.config_filename is None:
            self.config_filename = self.generate_config_filename()
        parser = ConfigParser()
        parser.read(self.config_filename)
        try:
            token = parser.get(section='auth', option='token')
        except NoSectionError:
            raise AMaaSException('Invalid AMaaS config file')
        return token
