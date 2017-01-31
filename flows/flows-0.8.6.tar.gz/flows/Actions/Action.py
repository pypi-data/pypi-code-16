#!/usr/bin/env python

'''
Action.py
Action superclasses
-------------------

Copyright 2016 Davide Mastromatteo
License: Apache-2.0
'''

import glob
import pickle
import time
from threading import Thread

import zmq

import flows.Global
import importlib
import importlib.util


class ActionInput:
    """
    Standard input for every action in flows
    """
    sender = ""
    receiver = ""
    message = ""
    file_system_event = None

    def __init__(self, event, message, sender, receiver="*"):
        super().__init__()
        self.message = message
        self.file_system_event = event
        self.sender = sender
        self.receiver = receiver


class Action(Thread):
    """
    Generic abstract class that should be subclassed to create
    custom action classes.
    """

    type = ""
    name = ""
    configuration = None
    context = None
    socket = None
    is_running = True
    monitored_input = None
    my_action_input = None

    #capture_own_messages = False
    #need_warmup = False

    def __init__(self, name, configuration, managed_input):
        super().__init__()

        # Set the action as a daemon
        self.daemon = True

        # Init the action instance variables
        self.monitored_input = managed_input
        self.configuration = configuration
        self.name = name

        # Launch custom configuration method
        self.on_init()

        # Start the action (as a thread, the run method will be executed)
        self.start()

    def get_input(self):
        """
        Get an input message from the socket
        """
        try:
            [_, msg] = self.socket.recv_multipart(
                flags=zmq.NOBLOCK)
            obj = pickle.loads(msg)
            return obj

        except Exception as new_exception:
            if new_exception.errno == zmq.EAGAIN:
                return None
            else:
                raise new_exception

    def on_init(self):
        """
        Initialization of the action, code to be executed before start
        """
        pass

    def on_cycle(self):
        """
        Main cycle of the action, code to be executed before the start of each cycle
        """
        pass

    def on_input_received(self, action_input=None):
        """
        Fire the current action
        """
        pass

    def on_stop(self):
        """
        Code to be executed before end
        """

    def send_output(self, output):
        """
        Send an output to the socket
        """
        flows.Global.MESSAGE_DISPATCHER.send_message(output)

    def send_message(self, output):
        """
        Send a message to the socket
        """

        file_system_event = None
        if self.my_action_input:
            file_system_event = self.my_action_input.file_system_event or None

        output_action = ActionInput(file_system_event,
                                    output,
                                    self.name,
                                    "*")

        flows.Global.MESSAGE_DISPATCHER.send_message(output_action)

    def stop(self):
        ''' Stop the current action '''
        self.is_running = False
        self.on_stop()

    def run(self):
        """
        Start the action
        """
        # Set the messaging infrastructure (0mq)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(
            flows.Global.CONFIG_MANAGER.subscriber_socket_address)
        # self.socket.setsockopt(zmq.SUBSCRIBE, b"")

        flows.Global.LOGGER.debug(
            "RUNNING - " + self.name + " " + str(len(self.monitored_input)))

        for tmp_monitored_input in self.monitored_input:
            sender = "*" + tmp_monitored_input + "*"
            flows.Global.LOGGER.debug(self.name + " is monitoring " + sender)
            self.socket.setsockopt(zmq.SUBSCRIBE, bytes(
                sender, 'utf-8'))

        while self.is_running:
            try:
                # time.sleep(ConfigManager.default_().sleep_interval)
                debug = self.name == "action to be logged"

                self.on_cycle()

                my_action_input = self.get_input()
                if my_action_input is None:
                    continue

                self.my_action_input = my_action_input

                # Do not consider action if it's not directed to you
                if my_action_input.receiver != "*" and my_action_input.receiver != self.name:
                    if debug:
                        flows.Global.LOGGER.info(
                            "**>" + my_action_input.receiver)
                        flows.Global.LOGGER.info("**>" + str(self.name))
                        flows.Global.LOGGER.info(str.format(
                            "{0}  ---> Not for me, sorry...", self.name))
                    continue

                # Elaborate only input from monitored input ...
                if my_action_input.sender not in self.monitored_input:
                    if debug:
                        flows.Global.LOGGER.info(
                            "++>" + my_action_input.sender)
                        flows.Global.LOGGER.info(
                            "++>" + str(self.monitored_input))
                        flows.Global.LOGGER.info(str.format("""{0}  ---> It does not seems
                                                to be interesting.... """, self.name))

                    # ... or the action is the specific receiver
                    if my_action_input.receiver != self.name:
                        if debug:
                            flows.Global.LOGGER.info(
                                "-->" + my_action_input.receiver)
                            flows.Global.LOGGER.info("-->" + self.name)
                            flows.Global.LOGGER.info(str.format("""{0}  ---> Definately, not interesting
                                                                for me, sorry...""", self.name))

                        continue

                # If the message has to be processed, exec
                if debug:
                    flows.Global.LOGGER.info(str.format("""{0}  ---> Ok, I'm in! Let me
                                            see what can I do...""", self.name))

                self.on_input_received(my_action_input)

                #output = self.on_input_received(my_action_input)
                # if output is None:
                #    continue

                # output_action = ActionInput(my_action_input.file_system_event,
                #                            output[0],
                #                            self.name,
                #                            output[1])
                # self.send_output(output_action)
            except Exception as exc:
                flows.Global.LOGGER.error(
                    "Error while running the action " + self.name + " \n " + str(exc))

    @staticmethod
    def create_action_for_code(action_code, name, configuration, managed_input):
        """
        Factory method to create an instance of an Action from an input code
        """
        # flows.Global.LOGGER.debug(str.format("Creating action of type {0} "
        #                                     "with name {1} and configuration {2}",
        #                                     action_code,
        #                                     name,
        #                                     configuration))

        #flows.Global.LOGGER.debug("...looking for action files")
        python_files = glob.glob("./**/Actions/*Action.py", recursive=True)
        #flows.Global.LOGGER.debug("done")

        import flows.Actions
        for filename in python_files:
            module_name = "flows.Actions." + filename[16:-3]
            importlib.import_module(module_name, package="flows.Actions")

        action = None

        for subclass in Action.__subclasses__():
            if subclass.type == action_code:
                action_class = subclass
                action = action_class(name, configuration, managed_input)
                flows.Global.LOGGER.info("...created action " + str(action))
                return action

        # if action is None:
        #    flows.Global.LOGGER.warning(str.format("Action type {0} has not been found."
        #                                           "The action {1} will be skipped.",
        #                                           action_code,
        #                                           name))

        return action
