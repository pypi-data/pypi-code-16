import os
import sys
import time
import logging

from .command import Command
logger = logging.getLogger(__name__)


class Profiles(Command):
    def __init__(self, *args, **kwargs):
        self._logger = logger
        super(Profiles, self).__init__(*args, **kwargs)

    def list(self, all=False):
        logger.debug('Going to list profiles..')
        all = self._config.faaspot.profiles
        return all.todict()

    def create(self, name, faaspot_host, username, password):
        logger.debug('Going to create a profile')
        if self._profile_exists(name):
            raise Exception("Command invalid. Profile `{0}` already exists".format(name))
        if not faaspot_host or not username or not password:
            raise Exception("Missing arguments. Please provide host, username and password")
        faaspot_port = 80
        host_data = faaspot_host.split(':')
        if len(host_data) == 2:
            faaspot_host, faaspot_port = host_data
        profile_data = {
            'host': faaspot_host,
            'port': faaspot_port,
            'username': username,
            'password': password
        }
        self._config.faaspot.profiles[name] = profile_data
        self._config.faaspot.profile = name
        self._config.save()
        return 'Current profile: {0}'.format(name)

    def update(self, name, faaspot_host, username, password):
        try:
            profile_name = name or self._config.faaspot.profile
            logger.debug('Going to update profile `{0}`'.format(profile_name))
            profile = self._get_profile_from_config(name)
            host, port = self._extract_host_info(faaspot_host)
            profile_data = {
                'host': host or profile.host,
                'port': port or profile.port,
                'username': username or profile.username,
                'password': password or profile.password
            }
            self._config.faaspot.profiles[name] = profile_data
            self._config.save()
            return 'Profile `{0}` updated successfully'.format(name)
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise

    def get(self, name):
        logger.debug('Going to return `{0}` profile info'.format(name))
        profile_name = name
        profile = self._get_profile_from_config(name)
        # profile = self._config.faaspot.profiles[profile_name]
        return '`{0}` profile data: {1}'.format(profile_name, profile)

    def use(self, name):
        logger.debug('Going to change current profile to: {0}'.format(name))
        _ = self._get_profile_from_config(name)
        self._config.faaspot.profile = name
        self._config.save()
        return 'Current profile: {0}'.format(name)

    def current(self):
        logger.debug('Going to return current profile info')
        profile_name = self._config.faaspot.profile
        profile = self._get_profile_from_config(profile_name)
        return 'Profile `{0}`: {1}'.format(profile_name, profile)

    def delete(self, name, force):
        if not force:
            raise Exception('Failed to delete profile, must supply --force flag')
        logger.debug('Going to delete profile `{0}`'.format(name))
        _ = self._get_profile_from_config(name)
        del self._config.faaspot.profiles[name]
        if self._config.faaspot.profile == name:
            self._config.faaspot.profile = ''
        self._config.save()
        return "Profile `{0}` deleted".format(name)

    def _get_profile_from_config(self, name):
        try:
            profile = self._config.faaspot.profiles[name]
        except KeyError:
            raise Exception('Failed retrieving profile `{0}` - '
                            'profile does not exist'.format(name))
        return profile

    def _profile_exists(self, name):
        try:
            _ = self._config.faaspot.profiles[name]
        except KeyError:
            return False
        return True

    @staticmethod
    def _extract_host_info(host):
        if not host:
            return None, None
        if ':' not in host:
            host += ':80'
        return host.split(':')
