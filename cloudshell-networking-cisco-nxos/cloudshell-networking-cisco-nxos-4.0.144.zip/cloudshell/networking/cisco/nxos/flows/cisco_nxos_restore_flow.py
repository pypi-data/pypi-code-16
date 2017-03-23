#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict

import time

from cloudshell.networking.cisco.cisco_command_actions import delete_file, copy, override_running, reload_device, \
    write_erase, reload_device_via_console
from cloudshell.networking.cisco.flow.cisco_restore_flow import CiscoRestoreFlow


class CiscoNXOSRestoreFlow(CiscoRestoreFlow):
    STARTUP_LOCATION = "startup-config"
    RUNNING_LOCATION = "running-config"
    BACKUP_STARTUP_LOCATION = "bootflash:backup-sc"
    TEMP_STARTUP_LOCATION = "bootflash:local-copy"

    def __init__(self, cli_handler, logger):
        super(CiscoNXOSRestoreFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name):
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
            reload_action_map = self._prepare_reload_act_map()

            if restore_method == "override":
                if self._cli_handler.cli_type.lower() != "console":
                    raise Exception(self.__class__.__name__,
                                    "Unsupported cli session type: {0}. Only Console allowed for restore override".format(
                                        self._cli_handler.cli_type.lower()))
                copy(session=enable_session, logger=self._logger, source=path,
                     destination=self.TEMP_STARTUP_LOCATION, vrf=vrf_management_name,
                     action_map=copy_action_map)
                write_erase(enable_session, self._logger)
                reload_device_via_console(enable_session, self._logger, action_map=reload_action_map)
                copy(session=enable_session, logger=self._logger, source=self.TEMP_STARTUP_LOCATION,
                     destination=self.RUNNING_LOCATION,
                     action_map=self._prepare_action_map(self.TEMP_STARTUP_LOCATION, self.RUNNING_LOCATION))
                time.sleep(5)
                copy(session=enable_session, logger=self._logger, source=self.RUNNING_LOCATION,
                     destination=self.STARTUP_LOCATION,
                     action_map=self._prepare_action_map(self.RUNNING_LOCATION, self.STARTUP_LOCATION), timeout=200)
            else:
                if "startup" in configuration_type:
                    raise Exception(self.__class__.__name__, "Restore of startup config in append mode is not supported")
                else:
                    copy(session=enable_session, logger=self._logger, source=path,
                         destination=configuration_type, vrf=vrf_management_name,
                         action_map=copy_action_map)

    def _prepare_reload_act_map(self):
        action_map = OrderedDict()
        # Proceed with reload? [confirm]
        action_map[r"[Aa]bort\s+[Pp]ower\s+[Oo]n\s+[Aa]uto\s+[Pp]rovisioning.*[\(\[].*[Nn]o[\]\)]"] = \
            lambda session, logger: session.send_line("yes", logger)
        action_map[r"[Ee]nter\s+system\s+maintenance\s+mode.*[\[\(][Yy](es)?\/[Nn](o)?[\)\]] "] = \
            lambda session, logger: session.send_line('n', logger)
        action_map[r"[Ss]tandby card not present or not [Rr]eady for failover]"] = \
            lambda session, logger: session.send_line('y', logger)
        action_map[r"[Pp]roceed with reload"] = lambda session, logger: session.send_line(' ', logger)
        action_map[r"reboot.*system"] = lambda session, logger: session.send_line('y', logger)
        action_map[r"[Ww]ould you like to enter the basic configuration dialog"] = \
            lambda session, logger: session.send_line('n', logger)
        action_map[r"[Dd]o you want to enforce secure password standard"] = \
            lambda session, logger: session.send_line('n', logger)
        action_map['[Ll]ogin:|[Uu]ser:|[Uu]sername:'] = lambda session, logger: session.send_line(
            self._cli_handler.username, logger)
        action_map['[Pp]assword.*:'] = lambda session, logger: session.send_line(
            self._cli_handler.password, logger)
        action_map[r"\[confirm\]"] = lambda session, logger: session.send_line('y', logger)
        action_map[r"continue"] = lambda session, logger: session.send_line('y', logger)
        action_map[r"\(y\/n\)"] = lambda session, logger: session.send_line('n', logger)
        action_map[r"[\[\(][Yy]es/[Nn]o[\)\]]"] = lambda session, logger: session.send_line('n', logger)
        action_map[r"[\[\(][Nn]o[\)\]]"] = lambda session, logger: session.send_line('n', logger)
        action_map[r"[\[\(][Yy]es[\)\]]"] = lambda session, logger: session.send_line('n', logger)
        action_map[r"[\[\(][Yy]/[Nn][\)\]]"] = lambda session, logger: session.send_line('n', logger)

        return action_map
