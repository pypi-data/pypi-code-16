"""
juju_helper
-----------

This module provides functions necessary for the Juju VNFM to communicate with Juju.
It uses mainly functions from the jujuclient and wraps them in functions needed for the Juju VNFM.
"""
# License: TODO
# Author: Thomas Briedigkeit

import logging
import ssl
import subprocess
import threading

import jujuclient.juju2.facades as facades
import tempfile
from jujuclient.juju2.environment import Environment

from utils.utils import raise_juju_exception

log = logging.getLogger('org.openbaton.python.vnfm.jujuvnfm')


class JujuRequestor:
    def __init__(self, vim_name):
        if '/' in vim_name:
            controller_name, model = vim_name.split('/')
        else:
            controller_name = vim_name
            model = 'default'

        # due to an SSLError that appears from time to time when connecting to a controller
        for attempt in range(0, 5):
            try:
                self.env = Environment.connect('{}:admin@local/{}'.format(controller_name, model))
                break
            except ssl.SSLError as ssl_error:
                if attempt == 4:
                    log.error(
                        'After five attempts the SSLError is still occurring. Looks like there is a real problem.')
                    raise ssl_error
                log.warning('SSLError occurred while connecting to the controller {}. Try one more time.'.format(
                    controller_name))

        if self.env is None:
            raise Exception('Could not retrieve Juju environment {}.'.format(controller_name))
        self.controller = facades.Client(self.env)
        if self.controller is None:
            raise Exception('Could not retrieve Juju Controller')
        self.application_client = facades.Application(self.env)
        if self.application_client is None:
            raise Exception('Could not retrieve application client')
        self.action_client = facades.Actions(self.env)

        if self.action_client is None:
            raise Exception('Could not retrieve action client.')

    lock = threading.Lock()

    def get_relations(self, app_name):
        return self.application_client.valid_relation_names(app_name)

    def add_relation(self, source_app_name, target_app_name):
        log.debug("Adding relation between %s and %s", source_app_name, target_app_name)
        self.application_client.add_relation(source_app_name, target_app_name)
        log.info("Added relation between %s and %s", source_app_name, target_app_name)

    def get_status(self, app_name=None):
        with self.lock:
            status = self.controller.status()
        if not app_name:
            return status
        else:
            try:
                return status.get('applications').get(app_name).get('status').get('status')
            except AttributeError as e:
                return None

    def trigger_action_on_charm(self, charm_name, action_name, params={}):
        """Trigger the execution of a specified action in a charm."""
        units = self.get_units(charm_name)
        unit_names = []
        for unit in units:
            unit_names.append(unit)

        with self.lock:  # TODO lock necessary?
            self.action_client.enqueue_units(unit_names, action_name, params)

    def trigger_action_on_units(self, unit_names, action_name, params={}):
        """Trigger the execution of a specified action in a charm."""
        with self.lock:  # TODO lock necessary?
            log.debug("Triggering action %s on unit(s) %s" % (action_name, unit_names))
            log.debug("result: %s" % self.action_client.enqueue_units(unit_names, action_name, params))

    def get_units(self, application_name, status=None):
        """Get the units of a deployed charm."""
        if status is None:
            status = self.get_status()
        applications = status.get('applications')
        if applications is None:
            return {}
        application = applications.get(application_name)
        if application is None:
            return {}
        units = application.get('units')
        return units

    def get_completed_actions(self, unit_names):
        with self.lock:
            completed = self.action_client.completed(unit_names)
        return completed

    def get_private_address_from_unit(self, unit_name):
        with self.lock:
            private_address_dict = self.controller.get_private_address(unit_name)
            if private_address_dict is not None:
                private_address = private_address_dict.get('private-address')
                if private_address is None:  # TODO handle this in a better way
                    private_address = private_address_dict.get('public-address')
        return private_address

    def get_public_address_from_unit(self, unit_name):
        with self.lock:
            public_address_dict = self.controller.get_public_address(unit_name)
        if public_address_dict is not None:
            public_address = public_address_dict.get('public-address')
        return public_address

    def get_machine_by_number(self, machine_number, status=None):
        if status is None:
            status = self.get_status()
        machines = status.get('machines')
        if machines is None:
            return None
        return machines.get(machine_number)

    def get_machine_number_by_unit_name(self, unit_name, status=None):
        if status is None:
            status = self.get_status()
        application_name = unit_name.split('/')[0]
        units = self.get_units(application_name, status)
        if units is None:
            return None
        unit = units.get(unit_name)
        if unit is None:
            return None
        return unit.get('machine')

    def get_machine_by_unit(self, unit_name, status=None):
        machine_number = self.get_machine_number_by_unit_name(unit_name, status)
        return self.get_machine_by_number(machine_number, status)

    def get_machine_numbers_by_application(self, application_name, status=None):
        if status is None:
            status = self.get_status()
        units = self.get_units(application_name, status)
        if units is None:
            return None
        machine_numbers = []
        for unit in units:
            machine_number = self.get_machine_number_by_unit_name(unit)
            if machine_number is not None:
                machine_numbers.append(machine_number)
        return machine_numbers

    def get_hostname(self, unit_name):
        machine = self.get_machine_by_unit(unit_name)
        if machine is None:
            return None
        return machine.get('instance-id')

    def get_machine_number_by_hostname(self, hostname, status=None):
        if status is None:
            status = self.get_status()
        machines = status.get('machines')
        if machines is None:
            return None
        for machine_number in machines:
            if machines.get('machine').get('instance-id') == hostname:
                return machine_number

    def get_unit_by_machine_number(self, machine_number, status=None):
        if status is None:
            status = self.get_status()
        applications = status.get('applications')
        for application in applications:
            units = applications.get(application).get('units')
            for unit in units:
                if units.get(unit).get('machine') == machine_number:
                    return unit

    def get_unit_by_hostname(self, hostname):
        """Used to get the unit that is associate to the machine with the given hostname.
        In this way we can associate a unit precisely to a vnfc_instance."""
        machine_number = self.get_machine_number_by_hostname(hostname)
        if machine_number is None:
            return None
        return self.get_unit_by_machine_number(machine_number)

    def get_ip_addresses_from_unit(self, unit_name, status=None):
        if status is None:
            status = self.get_status()
        machine = self.get_machine_by_unit(unit_name, status)
        if not machine:
            return []
        return machine.get('ip-addresses')

    def terminate_application(self, application_name, status=None):
        # check if application with this name is actually deployed, if not regard it as terminated
        if status is None:
            status = self.get_status()
        applications = status.get('applications')
        for application in applications:
            if application == application_name:
                # self.application_client = facades.Application(self.env)
                self.application_client.destroy_service(application_name)
                log.inof("Removed application %s" % application_name)
                return
        log.warning('Did not find application named {}. Regard this VNF as terminated.'.format(application_name))

    def machine_exists(self, check_number, status=None):
        if status is None:
            status = self.get_status()
        machines = status.get('machines')
        if machines is None:
            return False
        for machine_number in machines:
            if machine_number == check_number:
                return True
        return False

    def scale_out(self, application_name, machine_number=None):
        if machine_number is not None:
            if not self.machine_exists(machine_number):
                raise RuntimeError('Machine with number {} not found.'.format(machine_number))
        units = self.application_client.add_unit(application_name, machine_spec=machine_number)
        new_unit = units.get('units')[0]
        return new_unit

    def scale_in(self, application_name, vnfc_instance, machine_number=None):
        if machine_number is not None:
            if not self.machine_exists(machine_number):
                raise RuntimeError('Machine with number {} not found.'.format(machine_number))
            unit_name = self.get_unit_by_machine_number(machine_number)
        else:
            fip = vnfc_instance.get('floatingIps')[0].get('ip')
            units = self.get_units(application_name)
            for unit in units:
                log.debug("Unit to be removed is %s" % units[unit])
                unit_fip = self.get_public_address_from_unit(unit)
                log.debug("checking if unit public address %s == %s", unit_fip, fip)
                if fip == unit_fip:
                    unit_name = unit
                    machine_number = units[unit].get('machine')
                    break
        log.debug(
            "calling scale in for unit_name %s, and it should match machine number %s" % (unit_name, machine_number))
        self.remove_machine_force(machine_number)
        self.application_client.remove_units([unit_name])

    def remove_machine_force(self, machine_number):
        log.debug("juju remove-machine --force %s" % machine_number)
        output = subprocess.check_output(['juju', 'remove-machine', '--force', str(machine_number)],
                                         stderr=subprocess.PIPE)
        log.debug("Output of remove machine --force is %s", output)

    def deploy_local_charm(self, charm_dir_path, application_name, number_of_units, machine_number=None,
                           series='trusty'):
        """Deploy a charm from a local directory."""
        log.debug('Deploy charm for VNF ' + application_name)
        if machine_number is not None:
            if not self.machine_exists(machine_number):
                raise RuntimeError(
                    'Machine with number {} for deploying {} not found.'.format(machine_number, application_name))
        # workaround for ssl problems
        ssl._create_default_https_context = ssl._create_unverified_context
        # add a local charm directory to the environment
        res = self.env.add_local_charm_dir(charm_dir_path, series)
        # deploy the previously added local charm
        log.debug('machine_number: {}'.format(machine_number))
        deploy_res = self.application_client.deploy(application_name, res['charm-url'], number_of_units,
                                                    machine_spec=machine_number)
        log.debug('Deploying {} returned {}'.format(application_name, deploy_res))

    def deploy_from_charm_store(self, application_name, charm_type, number_of_units, series=None, conf_params=[],
                                machine_number=None):
        """Deploy a charm from the Juju charm store."""
        with tempfile.NamedTemporaryFile(mode='w+') as conf_yaml:
            command_array = ['juju', 'deploy']
            if machine_number:
                command_array.append('--to')
                command_array.append(str(machine_number))
            command_array.append('-n')
            command_array.append(str(number_of_units))
            if len(conf_params) > 0:
                command_array.append('--config')
                conf_yaml.write(charm_type + ':\n')
                conf_yaml.writelines(conf_params)
                command_array.append(conf_yaml.name)
            if series:
                command_array.append('--series')
                command_array.append(series)
            command_array.append(charm_type)
            command_array.append(application_name)
            log.debug('Deploy charm {} from the Juju charm store for VNF {}.'.format(charm_type, application_name))
            log.debug('Calling {}'.format(command_array))
            try:
                subprocess.check_output(command_array, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                raise_juju_exception(
                    'Could not deploy Charm {} for VNF {} from Charm Store. output is: {}'.format(charm_type,
                                                                                                  application_name,
                                                                                                  e.output))

    def wait_for_action(self, unit_name, param):
        pass


class ManualProvisioner(threading.Thread):
    def __init__(self, fip, application_name):
        super().__init__()
        self.fip = fip
        self.application_name = application_name
        self.output = None

    def run(self):
        log.info('Calling juju add-machine ssh:{}'.format(self.fip))
        p = subprocess.Popen(['juju', 'add-machine', 'ssh:{}'.format(self.fip)], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        self.output = (out + err).decode('utf-8')
