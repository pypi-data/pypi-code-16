#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.networking.devices.flows.cli_action_flows import RunCommandFlow
from cloudshell.networking.devices.runners.interfaces.run_command_runner_interface import RunCommandInterface


class RunCommandRunner(RunCommandInterface):
    def __init__(self, logger):
        """Create RunCommandOperations

        :param logger: QsLogger object
        """

        # ToDo: use as abstract methods
        self._cli_handler = None
        self._logger = logger

    def run_custom_command(self, custom_command):
        """ Execute custom command on device

        :param custom_command: command
        :return: result of command execution
        """

        run_command_flow = RunCommandFlow(self._cli_handler, self._logger)
        return run_command_flow.execute_flow(custom_command=custom_command)

    def run_custom_config_command(self, custom_command):
        """ Execute custom command in configuration mode on device

        :param custom_command: command
        :return: result of command execution
        """

        run_command_flow = RunCommandFlow(self._cli_handler, self._logger)
        return run_command_flow.execute_flow(custom_command=custom_command, is_config=True)
