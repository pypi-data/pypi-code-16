#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from cloudshell.networking.cisco.cisco_command_actions import delete_file, copy
from cloudshell.networking.cisco.flow.cisco_restore_flow import CiscoRestoreFlow
from cloudshell.networking.cisco.iosxr.cisco_ios_xr_custom_actions import load, replace_config, \
    validate_replace_config_success, validate_load_success


class CiscoIOSXRRestoreFlow(CiscoRestoreFlow):
    STARTUP_LOCATION = "nvram:startup-config"
    BACKUP_STARTUP_LOCATION = "bootflash:backup-sc"
    TEMP_STARTUP_LOCATION = "bootflash:local-copy"

    def __init__(self, cli_handler, logger):
        super(CiscoIOSXRRestoreFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param path: the path to the configuration file, including the configuration file name
        :param restore_method: the restore method to use when restoring the configuration file.
                               Possible Values are append and override
        :param configuration_type: the configuration type to restore. Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """

        if "-config" not in configuration_type:
            configuration_type += "-config"

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            copy_action_map = self._prepare_action_map(path, configuration_type)
            if "startup" in configuration_type:
                raise Exception(self.__class__.__name__, "Startup configuration is not supported by IOS-XR")

            elif "running" in configuration_type:
                if restore_method == "override":
                    with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                        load_result = load(config_session=config_session, logger=self._logger, source_file=path,
                                           vrf=vrf_management_name)
                        validate_load_success(load_result)
                        replace_result = replace_config(config_session=config_session, logger=self._logger)
                        validate_replace_config_success(replace_result)
            else:
                    copy(session=enable_session, logger=self._logger, source=path,
                         destination=configuration_type, vrf=vrf_management_name,
                         action_map=copy_action_map)
