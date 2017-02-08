from urlparse import urlparse

from enum import Enum

__author__ = 'Martin Borba - borbamartin@gmail.com'


class Environment(Enum):
    def __str__(self):
        return self.value

    @property
    def value(self):
        return self._name_

    TEST1, TEST2, TEST3, TEST4, DEV, QA, UAT, STAGING, PRODUCTION = range(9)


class EnvironmentUtil(object):
    indicators = {
        Environment.TEST1: ['test1'],
        Environment.TEST2: ['test2'],
        Environment.TEST3: ['test3'],
        Environment.TEST4: ['test4'],
        Environment.DEV: ['dev'],
        Environment.QA: ['qa'],
        Environment.UAT: ['uat'],
        Environment.STAGING: ['stage', 'staging'],
    }

    def __init__(self, base_url):
        _url_parser = urlparse(base_url)
        self.url_netloc = _url_parser.netloc

    def is_production_environment(self):
        """
        Checks if the current environment is production
        :return: True if currently in production , false otherwise
        """
        return self.get_current_environment() == Environment.PRODUCTION

    def get_current_environment(self):
        """
        Gets the current environment
        :return: An Environment Enum representing the environment
        """
        for env in self.indicators:
            if self._is_env_indicator_in_url(self.indicators[env]):
                return env

        return Environment.PRODUCTION

    def _is_env_indicator_in_url(self, env_indicators):
        return any(indicator in self.url_netloc for indicator in env_indicators)
