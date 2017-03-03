from os.path import join
from json import load, dump
from sys import stderr
from voluptuous import Schema
from voluptuous.error import MultipleInvalid
from xdg.BaseDirectory import save_config_path
from keyring import get_password, set_password
from prompt_toolkit import prompt
from gnusocial.accounts import verify_credentials
from gnusocial.utils import AuthenticationError
from .util import full_handle
from .validation import URLValidator
from .i18n import _
CONFIG_PATH = save_config_path('gscli')
CONFIG_FILE = join(CONFIG_PATH, 'config.json')
schema = Schema({
    'username': str,
    'server_url': str,
}, required=True)


class NoDefaultConfigError(Exception):
    pass


class Config:
    __filename = CONFIG_FILE
    __config = None

    def __init__(self, config=None, filename=None):
        if filename:
            self.__filename = filename
        if config:
            self.config = config
            self.save_config()
        else:
            self.load_config_file()

    def load_config_file(self, filename=None):
        if not filename:
            filename = CONFIG_FILE
        try:
            with open(filename) as f:
                config = load(f)
                schema(config)
                self.__filename = filename
                self.__config = config
        except FileNotFoundError as e:
            if filename == CONFIG_FILE:
                raise NoDefaultConfigError
            else:
                raise e
        except MultipleInvalid as e:
            print(_('Invalid config:'), str(e), file=stderr)
            quit(code=1)

    def __getitem__(self, name):
        if name == 'password':
            return get_password('gscli', self.handle)
        else:
            return self.__config[name]

    def __setitem__(self, name, value):
        if name == 'password':
            set_password('gscli', self.handle, value)
        else:
            self.__config[name] = value

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, config):
        schema(config)
        self.__config = config

    def save_config(self):
        with open(self.__filename, 'w') as f:
            dump(self.__config, f, indent=2, sort_keys=True)

    def __str__(self):
        return str(self.__config)

    def __repr__(self):
        return 'Config(%s)' % repr(self.__config)

    @property
    def handle(self):
        return full_handle(server_url=self['server_url'],
                           username=self['username'])


def create_default_config():
    while True:
        try:
            server_url = prompt(_('Enter server URL: '), validator=URLValidator())
            username = prompt(_('Enter username: '))
            handle = full_handle(username=username, server_url=server_url)
            password = prompt(_('Enter password: '), is_password=True)
            set_password('gscli', handle, password)
            config = {
                'username': username,
                'server_url': server_url
            }
            verify_credentials(**config, password=password)
        except AuthenticationError as e:
            print(e, file=stderr)
            continue
        c = Config(config=config)
        print(_('Configuration saved in {file}').format(file=CONFIG_FILE))
        return c
