#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import abstractproperty

from cloudshell.networking.devices.flows.cli_action_flows import RunCommandFlow
from cloudshell.networking.devices.runners.interfaces.state_runner_interface import StateOperationsInterface
from cloudshell.shell.core.context_utils import get_resource_name


class StateRunner(StateOperationsInterface):
    def __init__(self, logger, api, context):
        self._logger = logger
        self._api = api
        self._context = context
        self._resource_name = get_resource_name(context)
        # ToDo: use as abstract methods
        self._cli_handler = None

    @property
    def shutdown_flow(self):
        return None

    def health_check(self):
        """ Verify that device is accessible over CLI by sending ENTER for cli session """

        self._logger.info('Start health check on {} resource'.format(self._resource_name))
        api_response = 'Online'

        result = 'Health check on resource {}'.format(self._resource_name)
        try:
            health_check_flow = RunCommandFlow(self._cli_handler, self._logger)
            health_check_flow.execute_flow()
            result += ' passed.'
        except Exception:
            api_response = 'Error'
            result += ' failed.'

        try:
            self._api.SetResourceLiveStatus(self._resource_name, api_response, result)
        except Exception:
            self._logger.error('Cannot update {} resource status on portal'.format(self._resource_name))

        self._logger.info('Health check on {} resource completed'.format(self._resource_name))
        return result

    def shutdown(self):
        """ Shutdown device """
        output = None
        shutdown_flow = self.shutdown_flow
        if shutdown_flow:
            output = shutdown_flow.execute_flow()
        return output
