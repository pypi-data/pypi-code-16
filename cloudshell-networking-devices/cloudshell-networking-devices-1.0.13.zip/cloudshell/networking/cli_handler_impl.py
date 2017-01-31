#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.cli.cli import CLI
from cloudshell.cli.cli_service_impl import CommandModeContextManager

from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.networking.cli_handler_interface import CliHandlerInterface
from cloudshell.shell.core.context_utils import get_attribute_by_name, get_resource_address


class CliHandlerImpl(CliHandlerInterface):
    def __init__(self, cli, context, logger, api):
        """
        Helps to create cli handler
        :param cli:
        :type cli: CLI
        :param context:
        :param logger:
        :param api:
        :return:
        """
        self._cli = cli
        self._context = context
        self._logger = logger
        self._api = api

        # --------------------------------------------------------
        # the modes must be defined to trigger 'RunCustomCommand' as is
        self.enable_mode = None
        self.config_mode = None
        # --------------------------------------------------------

    @property
    def username(self):
        return get_attribute_by_name('User', self._context)

    @property
    def password(self):
        password = get_attribute_by_name(attribute_name='Password', context=self._context)
        return self._api.DecryptPassword(password).Value

    @property
    def resource_address(self):
        """Resource IP

        :return:
        """
        return get_resource_address(self._context)

    @property
    def port(self):
        """Connection port property, to open socket on

        :return:
        """
        return get_attribute_by_name('CLI TCP Port', self._context)

    @property
    def cli_type(self):
        """Connection type property [ssh|telnet|console|auto]

        :return:
        """
        return get_attribute_by_name('CLI Connection Type', self._context)

    def on_session_start(self, session, logger):
        """Perform some default commands when session just opened (like 'no logging console')

        :param session:
        :param logger:
        :return:
        """
        pass

    def _ssh_session(self):
        return SSHSession(self.resource_address, self.username, self.password, self.port, self.on_session_start)

    def _telnet_session(self):
        return TelnetSession(self.resource_address, self.username, self.password, self.port, self.on_session_start)

    def _new_sessions(self):
        if self.cli_type.lower() == SSHSession.SESSION_TYPE.lower():
            new_sessions = self._ssh_session()
        elif self.cli_type.lower() == TelnetSession.SESSION_TYPE.lower():
            new_sessions = self._telnet_session()
        else:
            new_sessions = [self._ssh_session(), self._telnet_session()]
        return new_sessions

    def get_cli_service(self, command_mode):
        """Use cli.get_session to open CLI connection and switch into required mode

        :param CommandMode command_mode: operation mode, can be default_mode/enable_mode/config_mode/etc.
        :return: created session in provided mode
        :rtype: CommandModeContextManager
        """
        return self._cli.get_session(self._new_sessions(), command_mode, self._logger)
