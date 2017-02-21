#!/usr/bin/env python

#
# Project:  juju-vnfm
# file:     juju_new_helper
# created:  17/02/2017 
#

"""
description goes here
"""
import asyncio
import logging
import subprocess
import threading
import time

__author__ = "lto"
__maintainer__ = "lto"

log = logging.getLogger('org.openbaton.python.vnfm.jujuvnfm.%s' % __name__)

model = None


async def get_unit(unit_name, model):
    return model.units.get(unit_name)


async def get_units(application_name, model, loop):
    application = get_application(application_name, model)
    return application.units


async def run_action_and_wait(unit_name, action_name, parameters=None, model=None, loop=None):
    action = run_action(unit_name, action_name, parameters, model, loop)
    # wait for the action to complete
    action = await action.wait()
    log.debug("action %s -> results: %s" % (action_name, action.results))


async def run_action(unit_name, action_name, parameters=None, model=None):
    log.debug('Running action %s on unit %s', action_name, unit_name)
    # unit.run() returns a juju.action.Action instance
    unit, model = await get_unit(unit_name, model)
    action = unit.run_action(action_name, parameters)
    return action, model


async def get_public_address_from_unit(unit_name, model=None, loop=None):
    return await get_unit(unit_name, model).data.get("public-address")


async def get_machine_by_number(machine_number, model):
    return model.machines.get(machine_number)


async def get_machine_number_by_unit_name(unit_name, model):
    return get_unit(unit_name, model).data.get("machine-id")


async def get_hostname_by_unit_name(unit_name, model):
    return get_unit(unit_name, model).data.get("name")


async def get_ip_addresses_from_unit(unit_name, model):
    unit = await get_unit(unit_name, model)
    return [unit.data.get('private-address'), unit.data.get('public-address')]


async def get_application(application_name, model):
    return model.applications.get(application_name), model


async def terminate_application(application_name, model):
    application, model = await get_application(application_name, model)
    if application is not None:
        application.destroy()
    return model


async def machine_exists(machine_number, model):
    machine, model = get_machine_by_number(machine_number, model)
    return machine is not None, model


async def scale_out(application_name, machine_number=None, unit_to_add_number=1, model=None):
    if machine_number is not None:
        exists, model = machine_exists(machine_number, model)
        if not exists:
            raise RuntimeError('Machine with number {} not found.'.format(machine_number))
    application, model = get_application(application_name, model)

    return application.add_unit(count=unit_to_add_number, to=str(machine_number)), model


async def deploy_local_charm(charm_dir_path, application_name, number_of_units, machine_number=None, model=None):
    application = await model.deploy(charm_dir_path,
                                     application_name,
                                     num_units=number_of_units,
                                     series='trusty',
                                     to=[dict(scope='#', directive=str(machine_number))])
    log.debug("deployed application: %s", application)
    return model


async def deploy_from_charm_store(application_name, charm_type, number_of_units, series=None, conf_params=[],
                                  machine_number=None, model=None):
    application = await model.deploy(charm_type,
                                     application_name,
                                     num_units=number_of_units,
                                     config=conf_params,
                                     series=series,
                                     to=[dict(scope='#', directive=str(machine_number))])
    log.debug("deployed application: %s", application)
    return model


class ManualProvisioner(threading.Thread):
    def __init__(self, fip, app_name):
        super().__init__()
        self.fip = fip
        self.output = None
        self.application_name = app_name

    def run(self):
        log.info('Calling juju add-machine ssh:{}'.format(self.fip))
        p = subprocess.Popen(['juju', 'add-machine', 'ssh:{}'.format(self.fip)], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        self.output = (out + err).decode('utf-8')


class MachineWaiter(threading.Thread):
    successful = True
    return_message = ''

    def __init__(self, machines, target_states, unwanted_states):
        super().__init__()
        self.machines = machines
        self.target_states = target_states
        self.unwanted_states = unwanted_states
        self.loop = asyncio.get_event_loop()
        self.successful = False

    def run(self):
        while True:
            if self.machines is None:
                raise Exception('Could not retrieve machines')

            time.sleep(1)
            machines_in_target_state = [m for m in self.machines if
                                        m.data.get("instance-status").get("current") in self.target_states]
            machines_in_unwanted_state = [m for m in self.machines if
                                          m.data.get("instance-status").get("current") in self.unwanted_states]
            if len(machines_in_unwanted_state) > 0:
                self.successful = False
                log.error("%s machine(s) in error state", len(machines_in_unwanted_state))
                break
            if len(machines_in_target_state) == len(self.machines):
                self.successful = True
                break