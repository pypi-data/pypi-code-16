import os
import logging
import inspect

from ..config import Config
from ..client.httpclient import HTTPClient

logger = logging.getLogger(__name__)

CONFIG_DIR = os.path.expanduser('~/.faaspot')
if not os.path.isdir(CONFIG_DIR):
    logger.debug('Creating config folder: {0}'.format(CONFIG_DIR))
    os.makedirs(CONFIG_DIR)
CONFIG_FILE = os.path.join(CONFIG_DIR, 'fasconf.yaml')


class NoExist(object):

    def __getattr__(self, attr):
        raise Exception("Failed: FaaSpot profile was not set. "
                        "Create a profile using profiles command.")


class Command(object):
    def __init__(self, *args, **kwargs):
        self._action = args[0] if len(args) else ''
        self._argument = kwargs
        self._name = self.__class__.__name__.lower()
        self._actions = dict()
        self._config = Config(CONFIG_FILE)
        self._register_instance_functions()
        if not self._config.faaspot.profiles:
            self._profile = self._config.faaspot.profiles
            self.api = NoExist()
            return
        self._profile = self._config.faaspot.profiles.get(self._config.faaspot.profile)
        if self._profile.get('token'):
            self.api = HTTPClient(host=self._profile.host,
                                  port=self._profile.port,
                                  token=self._profile.token)
        else:
            self.api = HTTPClient(host=self._profile.host,
                                  port=self._profile.port,
                                  username=self._profile.username,
                                  password=self._profile.password)

    @classmethod
    def register_class(cls):
        commands.register(cls.__name__.lower(), cls)

    def run_function(self):
        function = self._actions.get(self._action)
        if not function:
            raise Exception('Missing function `{0}`'.format(self._action))
        return function(**self._argument)

    def _register_instance_functions(self):
        all_methods = inspect.getmembers(self)
        for method_line in all_methods:
            method_name, method = method_line
            if inspect.isroutine(method):
                if not method_name.startswith('_'):
                    self._actions[method_name] = method


class Commands(object):
    def __init__(self):
        self._commands = {}

    def register(self, name, command):
        self._commands[name] = command

    def get(self, name):
        return self._commands.get(name)

commands = Commands()
