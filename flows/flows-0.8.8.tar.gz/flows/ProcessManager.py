#!/usr/bin/env python

'''
ProcessManager.py
Action handler class
--------------------

Copyright 2016 Davide Mastromatteo
License: Apache-2.0
'''

import time
import threading
from flows.Actions.Action import Action
import flows.Global


class ProcessManager:
    """
    Process Manager: the manager of all the managers in flows
    """
    _instance = None
    actions = []
    forwarder = None

    @staticmethod
    def default_instance():
        """For use like a singleton, return the existing instance of the object or a new instance"""
        if ProcessManager._instance is None:
            with threading.Lock():
                if ProcessManager._instance is None:
                    ProcessManager._instance = ProcessManager()

        return ProcessManager._instance

    def start(self):
        """ Start the processes """
        # Start the forwarding device for 0mq
        # self.forwarder = MessageForwarder().default_instance()
        # self.forwarder.start_forwarder()

        # start the message dispatcher
        _ = flows.Global.MESSAGE_DISPATCHER
        time.sleep(1)

        # start the actions
        self._start_actions()

    def stop(self):
        """ Stop all the processes """
        self._stop_actions()
        flows.Global.LOGGER.info("closing 0mq devices")
        # self.forwarder.default_instance().stop_forwarder()

    def restart(self):
        """ Restart all the processes """
        flows.Global.LOGGER.info("restarting flows")
        self._stop_actions()    # stop the old actions
        self.actions = []       # clear the action list
        self._start_actions()   # start the configured actions

    def _read_recipe(self, filename):
        configuration = flows.Global.CONFIG_MANAGER
        configuration.read_recipe(filename)

    def _start_action_for_section(self, section):
        flows.Global.LOGGER.debug("...section " + section)
        if section == "configuration":
            return

        # read the configuration of the action
        action_configuration = flows.Global.CONFIG_MANAGER.sections[
            section]

        if len(action_configuration) > 0:
            action_type = None

            if "type" in action_configuration:
                action_type = action_configuration["type"]

            new_managed_input = []
            action_input = None

            if "input" in action_configuration:
                action_input = action_configuration["input"]
                new_managed_input = (item.strip()
                                     for item in action_input.split(","))

            my_action = Action.create_action_for_code(action_type,
                                                      section,
                                                      action_configuration,
                                                      list(new_managed_input))

            if my_action is not None:
                self.actions.append(my_action)

    def _start_actions(self):
        flows.Global.LOGGER.info("starting actions")
        flows.Global.LOGGER.debug("... parsing recipe")
        for recipe in flows.Global.CONFIG_MANAGER.recipes:
            self._read_recipe(recipe)

        flows.Global.LOGGER.debug("... starting actions for section")

        # Create the Action
        my_sections = [
            section for section in flows.Global.CONFIG_MANAGER.sections]

        list(map(lambda x: self._start_action_for_section(x), my_sections))

    def _stop_actions(self):
        """ Stop all the actions """
        flows.Global.LOGGER.info("stopping actions")
        map(lambda x: x.stop(), self.actions)

        time.sleep(1)
