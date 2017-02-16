"""
juju_waiter
-----------
TODO
"""
# License: TODO
# Author: Thomas Briedigkeit

import logging

import time

import threading


log = logging.getLogger('org.openbaton.python.vnfm.jujuvnfm')

class MachineWaiter(threading.Thread):
    successful = True
    return_message = ''
    def __init__(self, juju_requestor, machine_list, target_states, unwanted_states):
        super().__init__()
        self.juju_requestor = juju_requestor
        self.machine_list = machine_list
        self.target_states = target_states
        self.unwanted_states = unwanted_states

    def run(self):
        finished = False
        while not finished:
            time.sleep(1)
            status = self.juju_requestor.get_status()
            machines = status.get('machines')
            if machines is None:
                raise Exception('Could not retrieve machines')

            finished = True
            machine_list_copy = self.machine_list.copy()
            for machine_number in self.machine_list:
                machine = machines.get(machine_number)
                counter = 0
                while machine is None:
                    if counter >= 5:
                        raise Exception('Could not get machine ' + machine)
                    log.debug('Could not get machine {} but maybe it is not started yet. Try again.'.format(machine_number))
                    time.sleep(1)
                    machine = machines.get(machine_number)
                    counter += 1
                agent_status = machine.get('agent-status')
                if agent_status is None:
                    raise Exception('Could not get agent status from machine ' + machine_number)
                machine_status = agent_status.get('status')
                if machine_status is None:
                    raise Exception('Could not get status of machine ' + machine_number)
                # log.debug('Machine {} is in status {}'.format(machine_number, machine_status))
                if machine_status in self.target_states:
                    log.debug('Machine {} is in state: {}'.format(machine_number, machine_status))
                    machine_list_copy.remove(machine_number)
                elif machine_status in self.unwanted_states:
                    log.error('Machine {} is in state {}'.format(machine_number, machine_status))
                    self.return_message += 'Machine {} is in state {}\n'.format(machine_number, machine_status)
                    self.successful = False
                else:
                    finished = False
            self.machine_list = machine_list_copy


class ActionWaiter(threading.Thread):
    successful = True
    return_message = ''

    def __init__(self, juju_requestor, unit_name, action_name):
        super().__init__()
        self.juju_requestor = juju_requestor
        self.unit_name = unit_name
        self.action_name = action_name

    def run(self):
        log.debug('Start waiting for action {} on {} to finish.'.format(self.action_name, self.unit_name))
        finished = False
        while not finished:
            time.sleep(1)
            completed_actions = self.juju_requestor.get_completed_actions([self.unit_name])
            actions = completed_actions.get('actions')[0].get('actions')
            if actions is None:
                pass
            else:
                found_action = None
                for action in actions:
                    if action.get('action').get('name') == self.action_name:
                        if not found_action or action.get('enqueued') > found_action.get('enqueued'):
                            found_action = action
                if not found_action:
                    continue   # TODO maybe raise an exception instead?
                log.debug(
                    '{} action in Unit {} is in state {}.'.format(self.action_name, self.unit_name, action.get('status')))
                if action.get('status') == 'completed':
                    finished = True
                elif action.get('status') == 'failed':
                    finished = True
                    self.return_message = '{} action failed'.format(self.action_name)
                    self.successful = False


class TerminationWaiter(threading.Thread):
    successful = True
    return_message = ''

    def __init__(self, juju_requestor, machine_number_list, unwanted_states):
        super().__init__()
        self.juju_requestor = juju_requestor
        self.machine_number_list = machine_number_list
        self.unwanted_states = unwanted_states

    def run(self):
        finished = False
        while not finished:
            time.sleep(1)
            status = self.juju_requestor.get_status()
            machines = status.get('machines')
            if machines is None:
                raise Exception('Could not retrieve machines')

            finished = True
            for machine_number in self.machine_number_list:
                machine = machines.get(machine_number)
                if machine is not None:
                    finished = False
                    agent_status = machine.get('agent-status')
                    if agent_status is None:
                        raise Exception('Could not get agent status from machine ' + machine_number)
                    machine_status = agent_status.get('status')
                    if machine_status is None:
                        raise Exception('Could not get status of machine ' + machine_number)
                    # log.debug('Machine {} is in status {}'.format(machine_number, machine_status))
                    if machine_status in self.unwanted_states:
                            self.return_message = 'Machine {} is in state {}'.format(machine_number, machine_status)
                            self.successful = False
                            finished = True