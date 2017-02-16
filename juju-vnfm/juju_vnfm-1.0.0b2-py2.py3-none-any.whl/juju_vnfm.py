"""
Juju VNFM
-----------

An adapter to integrate Juju into the Open Baton environment as a VNFM.

Supports python 2.7.12+ & 3.4+. ??? TODO

See the README for example usage.
"""
# License: TODO
# Author: Thomas Briedigkeit

import json
import logging
import logging.config
import os
import shutil
import stat
import tempfile
import threading
import time
import subprocess
import re
import uuid

import jujuvnfm.juju_helper as juju_helper
import jujuvnfm.juju_waiter as juju_waiter
from vnfm.sdk.AbstractVnfmABC import AbstractVnfm, start_vnfm_instances
from vnfm.sdk.exceptions import PyVnfmSdkException
from vnfm.sdk.utils.Utilities import get_nfv_message, str2bool

log = logging.getLogger('org.openbaton.python.vnfm.jujuvnfm')


class JujuVnfm(AbstractVnfm):
    juju_command_line_semaphore = threading.Semaphore()
    deploy_store_charm_semaphore = threading.Semaphore()

    def get_params(self, vnfr, unit_ip_addresses, lifecycle_script, dependency=None):
        """Get the parameters that shall be passed to an action.
        Parameters contain out of the box parameters like the hostname and ips, configuration parameters and parameters from dependencies.

            Args:
                vnfr (dict): The VNFR from which the dependencies shall be etracted.
                unit_ip_addresses ([str]): The ips of the unit so that the corresponding VNFC instance can be found.
                lifecycle_script (str): Name of the lifecycle script that shall be executed.
                dependency (dict): The dependencies that were contained in the MODIFY message from the NFVO.

            Returns:
                [dict]: The list of parameters, each ready to pass to a Juju action.
                If dependencies were passed and the source has more than one VNFC instance, the list will contain more than one item.

            """
        params = {'scriptname': lifecycle_script}

        # create dependencies structure
        dependency_parameter_list = []
        source_type = lifecycle_script.split('_')[0]

        log.debug("dependency is: %s" % dependency)

        if dependency is not None:
            # foreign config from vnf dep
            conf_parameters = dependency.get('parameters')
            conf_paramters_list = []
            log.debug("confParamters is: %s" % conf_parameters)
            parameter_object = conf_parameters.get(source_type).get('parameters')
            log.debug("parameter_object is %s" % parameter_object)
            conf_dependencies = ''
            for k in parameter_object:
                value = parameter_object.get(k)
                if value is not None and value != '':
                    conf_dependencies += 'export {}_{}={}\n'.format(source_type, k, value)
            log.debug("adding to script a parameter: \n%s" % conf_dependencies)
            conf_paramters_list.append(conf_dependencies)

            # extracting from vnfcParameters (dynamic such as ips)
            vnfc_parameters = dependency.get('vnfcParameters')
            parameter_object = vnfc_parameters.get(source_type).get('parameters')
            if len(parameter_object) > 0:
                for id in parameter_object:
                    parameters = parameter_object.get(id).get('parameters')
                    dependencies = conf_dependencies
                    for parameter in parameters:
                        value = parameters.get(parameter)
                        if value is not None and value != '':
                            dependencies += 'export {}_{}={}\n'.format(source_type, parameter, value)
                    dependency_parameter_list.append(dependencies)
            else:
                dependency_parameter_list.append(conf_dependencies)

            log.debug("Final parameter list coming from nfvo is: \n%s" % conf_dependencies)

        # target config from vnf
        configuration_params = ''
        configurations = vnfr.get('configurations')
        for conf_param in configurations.get('configurationParameters'):
            conf_key = conf_param.get('confKey')
            value = conf_param.get('value')
            configuration_params += 'export {}={}\n'.format(conf_key, value)
        params['configuration'] = configuration_params

        out_of_the_box_params = ''
        # fill out of the box params from target vnf
        if not unit_ip_addresses:
            log.warning('No ip addresses were passed')
            return params
        for vdu in vnfr.get('vdu'):
            vim_instance_name = vdu.get('vimInstanceName')
            vnfc_instances = vdu.get('vnfc_instance')
            found_vnfc = False  # for breaking out of two for loops
            for vnfc_instance in vnfc_instances:
                if found_vnfc:
                    break
                for ip in vnfc_instance.get('ips'):
                    if ip.get(
                            'ip') in unit_ip_addresses:  # found the vnfc_instance for the unit specified by its ip addresses
                        out_of_the_box_params += 'export hostname={}\n'.format(vnfc_instance.get('hostname'))
                        for floating_ip in vnfc_instance.get('floatingIps'):
                            out_of_the_box_params += 'export {}_floatingIp={}\n'.format(floating_ip.get('netName'),
                                                                                        floating_ip.get('ip'))
                        for ip in vnfc_instance.get('ips'):
                            out_of_the_box_params += 'export {}={}\n'.format(ip.get('netName'), ip.get('ip'))
                        params['outOfTheBoxParams'] = out_of_the_box_params
                        found_vnfc = True
                        break

        params_list = []
        if len(dependency_parameter_list) > 0:
            for dep in dependency_parameter_list:
                params_with_dependencies = params.copy()
                params_with_dependencies['dependencies'] = dep
                params_list.append(params_with_dependencies)
        else:
            params_list.append(params)

        log.debug("final param list: %s" % params_list)
        return params_list

    def on_message(self, body):
        """
        This message is in charge of dispaching the message to the right method
        :param body:
        :return:
        """

        # for python 2 and 3 compatibility
        try:
            msg = json.loads(body)
        except TypeError:
            msg = json.loads(body.decode('utf-8'))

        try:
            action = msg.get("action")
            log.debug("Action is %s" % action)
            vnfr = msg.get('virtualNetworkFunctionRecord')
            if not vnfr:
                vnfr = msg.get('vnfr')
            nfv_message = None
            if action == "INSTANTIATE":
                extension = msg.get("extension")
                keys = msg.get("keys")
                log.debug("Got these keys: %s" % keys)
                vim_instances = msg.get("vimInstances")
                vnfd = msg.get("vnfd")
                vnf_package = msg.get("vnfPackage")
                vlrs = msg.get("vlrs")
                vnfdf = msg.get("vnfdf")
                # if vnf_package:
                #     if vnf_package.get("scriptsLink") is None:
                #         scripts = vnf_package.get("scripts")
                #     else:
                #         scripts = vnf_package.get("scriptsLink")
                vnfr = self.create_vnf_record(vnfd, vnfdf.get("flavour_key"), vlrs, vim_instances, extension)

                grant_operation = self.grant_operation(vnfr)
                vnfr = grant_operation["virtualNetworkFunctionRecord"]
                vim_instances = grant_operation["vduVim"]

                if str2bool(self._map.get("allocate", 'True')):
                    log.debug("Extensions are: %s" % extension)
                    vnfr = self.allocate_resources(vnfr, vim_instances, keys, **extension).get(
                        "vnfr")
                vnfr = self.instantiate(vnf_record=vnfr, vnf_package=vnf_package, vim_instances=vim_instances)

            if action == "MODIFY":
                vnfr = self.modify(vnf_record=vnfr, dependency=msg.get("vnfrd"))
            if action == "START":
                vnfr = self.start_vnfr(vnf_record=vnfr)
            if action == "ERROR":
                vnfr = self.handleError(vnf_record=vnfr)
            if action == "RELEASE_RESOURCES":
                vnfr = self.terminate(vnf_record=vnfr)
            if action == 'SCALE_OUT':
                component = msg.get('component')
                # vnf_package = msg.get('vnfPackage')
                dependency = msg.get('dependency')
                mode = msg.get('mode')
                # extension = msg.get('extension')

                if str2bool(self._map.get("allocate", 'True')):
                    scaling_message = get_nfv_message('SCALING', vnfr, user_data=self.get_user_data())
                    log.debug('The NFVO allocates resources. Send SCALING message.')
                    result = self.exec_rpc_call(json.dumps(scaling_message))
                    log.debug('Received {} message.'.format(result.get('action')))
                    vnfr = result.get('vnfr')

                vnfr = self.scale_out(vnfr, component, None, dependency)
                new_vnfc_instance = None
                for vdu in vnfr.get('vdu'):
                    for vnfc_instance in vdu.get('vnfc_instance'):
                        if vnfc_instance.get('vnfComponent').get('id') == component.get('id'):
                            if mode == 'STANDBY':
                                vnfc_instance['state'] = 'STANDBY'
                            new_vnfc_instance = vnfc_instance
                if new_vnfc_instance == None:
                    raise PyVnfmSdkException('Did not find a new VNFCInstance after scale out.')
                nfv_message = get_nfv_message('SCALED', vnfr, new_vnfc_instance)
            if action == 'SCALE_IN':
                vnfr = self.scale_in(vnfr, msg.get('vnfcInstance'))
                # nfv_message = get_nfv_message('SCALED', vnfr, TODO)

            if len(vnfr) == 0:
                raise PyVnfmSdkException("Unknown action!")
            if nfv_message == None:
                nfv_message = get_nfv_message(action, vnfr)
            return nfv_message
        except PyVnfmSdkException as exception:
            nfv_message = get_nfv_message('ERROR', vnfr, exception=exception)
            return nfv_message

    def notifyChange(self):
        pass

    def updateSoftware(self):
        pass

    def startVNFCInstance(self, vnf_record, vnfc_instance):
        pass

    def start_vnfr(self, vnf_record):
        vnf_name = vnf_record.get('name')

        # for Charms from the Charm Store no start action has to be executed
        # TODO consider checking if the Charms are started
        if vnf_record.get('type').startswith('juju-charm-store'):
            return vnf_record

        # trigger start action
        for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'START'):
            log.debug('Trigger execution of {} on {}'.format(lifecycle_script, vnf_name))

            wait_action_threads = []
            for vdu in vnf_record.get('vdu'):
                application_name = vnf_name + vdu.get('id').replace('-', '')
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_helper.JujuRequestor(vim)
                units = juju_requestor.get_units(application_name)
                for unit_name in units:
                    params = self.get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
                                             lifecycle_script)
                    juju_requestor.trigger_action_on_units([unit_name], 'start', params=params[0])
                for unit_name in units:
                    action_waiter = juju_waiter.ActionWaiter(juju_requestor, unit_name, 'start')
                    wait_action_threads.append(action_waiter)
            for t in wait_action_threads:
                t.start()
            for t in wait_action_threads:
                t.join()
                if not t.successful:
                    log.error(t.return_message)
                    raise PyVnfmSdkException('{} script failed'.format(lifecycle_script))
                log.debug('{} finished on {}'.format(lifecycle_script, application_name))
        log.info('Start finished for {}'.format(vnf_name))

        return vnf_record

    def terminate(self, vnf_record):  # extract information from the vnfr
        vnf_name = vnf_record.get('name')

        # for Charms from the Charm Store no terminate action has to be executed
        if not vnf_record.get('type').startswith('juju-charm-store'):
            for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'TERMINATE'):
                log.debug('Trigger execution of {} on {}'.format(lifecycle_script, vnf_name))

                wait_action_threads = []
                for vdu in vnf_record.get('vdu'):
                    application_name = vnf_name + vdu.get('id').replace('-', '')
                    vim = vdu.get('vimInstanceName')[0]
                    juju_requestor = juju_helper.JujuRequestor(vim)
                    units = juju_requestor.get_units(application_name)
                    for unit_name in units:
                        params = self.get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
                                                 lifecycle_script)
                        juju_requestor.trigger_action_on_units([unit_name], 'terminate', params=params[0])
                    for unit_name in units:
                        action_waiter = juju_waiter.ActionWaiter(juju_requestor, unit_name, 'terminate')
                        wait_action_threads.append(action_waiter)
                for t in wait_action_threads:
                    t.start()
                for t in wait_action_threads:
                    t.join()
                    if not t.successful:
                        log.error(t.return_message)
                        raise PyVnfmSdkException('{} script failed'.format(lifecycle_script))
                    log.debug('{} finished on {}'.format(lifecycle_script, application_name))
            log.info('Terminate finished for {}'.format(vnf_name))

        wait_termination_threads = []
        for vdu in vnf_record.get('vdu'):
            application_name = vnf_name + vdu.get('id').replace('-', '')
            vim = vdu.get('vimInstanceName')[0]
            juju_requestor = juju_helper.JujuRequestor(vim)
            machine_numbers = juju_requestor.get_machine_numbers_by_application(application_name)
            juju_requestor.terminate_application(application_name)
            termination_waiter = juju_waiter.TerminationWaiter(juju_requestor, machine_numbers, 'error')
            wait_termination_threads.append(termination_waiter)

        for t in wait_termination_threads:
            t.start()
        for t in wait_termination_threads:
            t.join()
            if not t.successful:
                log.error('Termination of {} failed. '.format(application_name) + t.return_message)
                raise PyVnfmSdkException('Termination of {} failed. '.format(vnf_name) + t.return_message)
            log.debug('Termination of {} finished.'.format(application_name))
        log.debug('Termination of {} finished.'.format(vnf_name))
        return vnf_record

    # TODO handle vnfcParameters
    def modify(self, vnf_record, dependency):
        # extract information from the vnfr
        vnf_name = vnf_record.get('name')

        # for Charms from the Charm Store no modify action has to be executed
        if vnf_record.get('type').startswith('juju-charm-store'):
            return vnf_record

        # get units of vnf and trigger modify action
        for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'CONFIGURE'):
            log.debug('Trigger execution of {} on {}'.format(lifecycle_script, vnf_name))
            vnfcParameters = dependency.get('vnfcParameters')
            source_type = lifecycle_script.split('_')[0]
            source_parameters = vnfcParameters.get(source_type)
            if not source_parameters:
                # this lifecycle script does not start with the type of a dependency source so skip it
                continue
            number_of_executions = len(
                source_parameters.get('parameters'))  # the number of source VNFC instances for this script
            log.debug('Number of executions for {}: {}'.format(lifecycle_script, number_of_executions))
            wait_action_threads = []
            for vdu in vnf_record.get('vdu'):
                application_name = vnf_name + vdu.get('id').replace('-', '')
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_helper.JujuRequestor(vim)
                units = juju_requestor.get_units(application_name)
                for i in range(0, number_of_executions):
                    for unit_name in units:
                        params_list = self.get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
                                                      lifecycle_script, dependency)
                        juju_requestor.trigger_action_on_units([unit_name], 'configure', params=params_list[i])
                for unit_name in units:
                    action_waiter = juju_waiter.ActionWaiter(juju_requestor, unit_name, 'configure')
                    wait_action_threads.append(action_waiter)
            for t in wait_action_threads:
                t.start()
            for t in wait_action_threads:
                t.join()
                if not t.successful:
                    log.error(t.return_message)
                    raise PyVnfmSdkException('{} script failed'.format(lifecycle_script))
                log.debug('{} finished on {}'.format(lifecycle_script, vnf_name))
        log.info('Modify finished for {}'.format(vnf_name))
        return vnf_record

    def stop(self, vnf_record):
        pass

    def handleError(self, vnf_record):
        pass

    def query(self):
        pass

    def upgradeSoftware(self):
        pass

    def stopVNFCInstance(self, vnf_record, vnfc_instance):
        pass

    def heal(self, vnf_record, vnf_instance, cause):
        pass

    def scale_out(self, vnf_record, vnf_component, scripts, dependency):
        # get the vim on which to create the new vnfc_instance
        vim_name = None
        vnf_type = vnf_record.get('type')
        deploy_from_charm_store = vnf_type.startswith('juju-charm-store')
        used_vdu = None
        for vdu in vnf_record.get('vdu'):
            for vnfc in vdu.get('vnfc'):
                if vnfc.get('id') == vnf_component.get('id'):
                    vim_name = vdu.get('vimInstanceName')[0]
                    used_vdu = vdu
        if vim_name is None:
            raise PyVnfmSdkException('Could not find a vim instance on which to perform the scale out')
        # extract information from the vnfr
        vnf_name = vnf_record.get('name')
        juju_requestor = juju_helper.JujuRequestor(vim_name)
        application_name = vnf_name + used_vdu.get('id').replace('-', '')

        # TODO if resource allocation is done on NFVO side, take over the VMs with Juju
        if str2bool(self._map.get("allocate", 'True')):
            log.debug('NFVO allocates resources for scale out.')
            new_vnfc_instance = None
            for vdu in vnf_record.get('vdu'):
                for vnfc_instance in vdu.get('vnfc_instance'):
                    if vnfc_instance.get('vnfComponent').get('id') == vnf_component.get('id'):
                        new_vnfc_instance = vnfc_instance
            if new_vnfc_instance == None:
                raise PyVnfmSdkException('Did not find a new VNFCInstance after scale out.')

            floating_ip_list = new_vnfc_instance.get('floatingIps')
            if len(floating_ip_list) == 0:
                raise RuntimeError(
                    'Not all VNFC instances of {} have floating ips. This is a requirement for using the Juju-VNFM with resource allocation on the NFVO side.'.format(
                        vnf_name))
            fip = floating_ip_list[0].get('ip')

            manual_provisioner = juju_helper.ManualProvisioner(fip, application_name)
            time.sleep(20)
            with self.juju_command_line_semaphore:
                log.info('Calling juju switch {}'.format(vim_name.replace('/', ':')))
                res = subprocess.call(['juju', 'switch', vim_name.replace('/', ':')])
                log.info('Exit status: {}'.format(res))
                manual_provisioner.start()
                time.sleep(5)
            manual_provisioner.join()
            output = manual_provisioner.output
            machine_number = None
            for line in output.splitlines():
                if 'created machine' in line:
                    machine_number = re.findall('\d+', line)[0]
                    application_name = manual_provisioner.application_name
                    log.info('Added machine {}'.format(machine_number))
            if machine_number is None:
                raise RuntimeError(
                    'Could not add the existing machine {} to Juju. This is the output: {}.'.format(fip,
                                                                                                    output))
            new_unit_name = juju_requestor.scale_out(application_name, machine_number=machine_number)
        else:
            log.debug('Juju-VNFM allocates resources for scale out.')
            new_unit_name = juju_requestor.scale_out(application_name)
            new_machine_number = juju_requestor.get_machine_number_by_unit_name(new_unit_name)
            machine_waiter = juju_waiter.MachineWaiter(juju_requestor, [new_machine_number], ['started'], ['error'])
            machine_waiter.start()
            machine_waiter.join()
            log.debug('Unit {} created and machine {} started'.format(new_unit_name, new_machine_number))

            # inject ips and hostname
            private = juju_requestor.get_private_address_from_unit(new_unit_name)
            public = juju_requestor.get_public_address_from_unit(new_unit_name)
            hostname = juju_requestor.get_hostname(new_unit_name)
            new_vnfc_instance = {}
            new_vnfc_instance['vim_id'] = 'TODO'  # TODO is there a way to get this id?
            new_vnfc_instance['vc_id'] = vnf_component.get('id')  # TODO the generic assigns another id, who is wrong?
            new_vnfc_instance['hostname'] = hostname
            new_vnfc_instance['vnfComponent'] = vnf_component
            new_vnfc_instance['connection_point'] = []
            for connection_point in vnf_component.get('connection_point'):
                new_connection_point = {}
                for key in connection_point:
                    if not key == 'id':
                        new_connection_point[key] = connection_point.get(key)
                new_vnfc_instance.get('connection_point').append(new_connection_point)

            vnf_record['vnf_address'] += private

            floating_ips = []
            ips = []
            for connection_point in new_vnfc_instance.get('connection_point'):
                if 'floatingIp' in connection_point and not connection_point.get(
                        'floatingIp') == None and not connection_point.get('floatingIp') == '':
                    floating_ips.append({'netName': connection_point.get('virtual_link_reference'),
                                         'ip': public})
                ips.append(({'netName': connection_point.get('virtual_link_reference'),
                             'ip': private}))

            new_vnfc_instance['floatingIps'] = floating_ips
            new_vnfc_instance['ips'] = ips
            new_vnfc_instance['id'] = str(uuid.uuid1())

            used_vdu.get('vnfc_instance').append(new_vnfc_instance)

        if deploy_from_charm_store:
            return vnf_record

        for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'INSTANTIATE'):
            log.debug('Trigger execution of {} on {}'.format(lifecycle_script, application_name))

            params = self.get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(new_unit_name),
                                     lifecycle_script)
            juju_requestor.trigger_action_on_units([new_unit_name], 'instantiate', params=params[0])

            action_waiter = juju_waiter.ActionWaiter(juju_requestor, new_unit_name, 'instantiate')
            action_waiter.start()
            action_waiter.join()
            if not action_waiter.successful:
                log.error(action_waiter.return_message)
                raise PyVnfmSdkException('{} script failed in INSTANTIATE'.format(lifecycle_script))
            log.debug('{} finished on {}'.format(lifecycle_script, application_name))
        log.debug('Instantiate scripts finished for {}'.format(vnf_name))

        for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'CONFIGURE'):
            log.debug('Trigger execution of {} on {}'.format(lifecycle_script, application_name))
            vnfcParameters = dependency.get('vnfcParameters')
            source_type = lifecycle_script.split('_')[0]
            source_parameters = vnfcParameters.get(source_type)
            if not source_parameters:
                # this lifecycle script does not start with the type of a dependency source so skip it
                continue
            number_of_executions = len(
                source_parameters.get('parameters'))  # the number of source VNFC instances for this script
            log.debug('Number of executions for {}: {}'.format(lifecycle_script, number_of_executions))
            for i in range(0, number_of_executions):
                params_list = self.get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(new_unit_name),
                                              lifecycle_script, dependency)
                juju_requestor.trigger_action_on_units([new_unit_name], 'configure', params=params_list[i])
                action_waiter = juju_waiter.ActionWaiter(juju_requestor, new_unit_name, 'configure')
                action_waiter.start()
                action_waiter.join()
                if not action_waiter.successful:
                    raise PyVnfmSdkException(
                        '{} script failed: {}'.format(lifecycle_script, action_waiter.return_message))
            log.debug('{} finished on {}'.format(lifecycle_script, application_name))
        log.debug('Configure scripts finished for {}'.format(vnf_name))

        # TODO check for STANDBY
        for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'START'):
            log.debug('Trigger execution of {} on {}'.format(lifecycle_script, application_name))

            params = self.get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(new_unit_name),
                                     lifecycle_script)
            juju_requestor.trigger_action_on_units([new_unit_name], 'start', params=params[0])

            action_waiter = juju_waiter.ActionWaiter(juju_requestor, new_unit_name, 'start')
            action_waiter.start()
            action_waiter.join()
            if not action_waiter.successful:
                raise PyVnfmSdkException(
                    '{} script failed in START: {}'.format(lifecycle_script, action_waiter.return_message))
            log.debug('{} finished on {}'.format(lifecycle_script, application_name))
        log.debug('Start scripts finished for {}'.format(vnf_name))

        return vnf_record

    def scale_in(self, vnf_record, vnfc_instance):
        '''The vnfc_instance specifies the vnfc that should be removed.
        The vnfr specifies the vnf that should execute the SCALE_OUT event.'''
        hostname = vnfc_instance.get('hostname')
        #  if '/' in vim_instance_name:
        #     controller_name, model = vim_instance_name.split('/')
        #     env = juju_helper.get_environment(controller_name, model)
        # else:
        #     env = juju_helper.get_environment(vim_instance_name) TODO we need the name of the vim on which the vnfc runs
        # TODO trigger SCALE_IN lifecycle event and stop the machine that is identified by the hostname
        log.warning('Scale in is not yet implemented...')
        return vnf_record

    def create_charm(self, vnf_name, vnf_lifecycle_events, vnf_package):
        log.debug('The VNFR {} has the following lifecycle events:'.format(vnf_name))
        for lifecycle_event in vnf_lifecycle_events:
            log.debug(' * ' + lifecycle_event.get('event'))

        # create a temporary directory for the charm
        tmp_charm_dir = tempfile.mkdtemp()
        os.mkdir(tmp_charm_dir + '/actions')
        os.mkdir(tmp_charm_dir + '/scripts')
        os.mkdir(tmp_charm_dir + '/hooks')

        with open(tmp_charm_dir + '/metadata.yaml', 'w+') as metadata_yaml:
            metadata_yaml.write(('name: {}\n' +
                                 'description: Charm created by the Juju-VNFM\n' +
                                 'summary: Charm created by the Juju-VNFM\n').format(vnf_name))

        # add Juju action scripts and actions.yaml for the Open Baton lifecycle events
        with open(tmp_charm_dir + '/actions.yaml', 'w') as actions_yaml:
            for lifecycle_event in vnf_lifecycle_events:
                event = lifecycle_event.get('event').lower()
                with open(tmp_charm_dir + '/actions/' + event, 'w') as action:
                    action.write(
                        '#!/bin/bash\ncd /opt/openbaton/scripts\n$(action-get dependencies)\n$(action-get '
                        'configuration)\n$(action-get outOfTheBoxParams)\nscript=$(action-get scriptname)\necho "$('
                        'date +\'%Y-%m-%d %T\') start executing $script" >> /var/log/openbaton/scriptLog\n./$script '
                        '&>> /var/log/openbaton/scriptLog\necho "$(date +\'%Y-%m-%d %T\') finished executing $script" '
                        '>> /var/log/openbaton/scriptLog\n')

                    os.chmod(action.name, stat.S_IRWXU | stat.S_IXOTH)
                actions_yaml.write(
                    ('{0}:\n  description: execute the lifecycle scripts for the {0} event\n' +
                     '  params:\n    dependencies:\n      type: string\n' +
                     '    outOfTheBoxParams:\n      type: string\n' +
                     '    configuration:\n      type: string\n' +
                     '    scriptname:\n      type: string\n').format(event))

        # in cases where the VNFD is not created from a VNF package and does not contain a scriptsLink
        if not vnf_package:
            log.debug('No VNF package provided')
            with open(tmp_charm_dir + '/hooks/install', 'w') as install_hook:
                install_hook.write(
                    '#!/bin/bash\nmkdir -p /var/log/openbaton\nmkdir -p /opt/openbaton/scripts')
            return tmp_charm_dir

        # get the lifecycle scripts from the VNFPackage and store them in the charm directory
        scripts = vnf_package.get("scriptsLink")
        if scripts is not None:
            # handle scripts in a git repo TODO find a way not to rely on GitPython since it requires git to be installed!!
            log.debug('Scripts are provided by a link: {}'.format(scripts))
            # add a install hook for getting the lifecycle scripts
            with open(tmp_charm_dir + '/hooks/install', 'w') as install_hook:
                install_hook.write(
                    '#!/bin/bash\napt-get install -y git\nmkdir -p /var/log/openbaton\nmkdir -p /opt/openbaton\ncd /opt/openbaton\ngit clone {}\nmv $(ls -1) scripts\nchmod -R +x /opt/openbaton/scripts/*'.format(
                        scripts))
        else:
            # handle scripts in package
            scripts = vnf_package.get("scripts")
            for script in scripts:
                payload = script.get('payload')
                name = script.get('name')
                content = bytearray(payload).decode('utf-8')
                with open(tmp_charm_dir + '/scripts/{}'.format(name), 'w') as script_file:
                    script_file.write(content)
                    os.chmod(script_file.name, stat.S_IRWXU | stat.S_IXOTH)
                # add a install hook for copying the lifecycle scripts into /opt/openbaton/scripts on the deployed machine
                with open(tmp_charm_dir + '/hooks/install', 'w') as install_hook:
                    install_hook.write(
                        '#!/bin/bash\nmkdir -p /var/log/openbaton\nmkdir -p /opt/openbaton\nmv scripts /opt/openbaton/scripts\nchmod -R +x /opt/openbaton/scripts/*')
            if scripts is None:
                raise ValueError('There are no scripts provided in the VNFPackage for the VNF %s' % vnf_name)
            log.debug('Scripts are provided by the VNFPackage')

        return tmp_charm_dir

    def instantiate(self, vnf_record, vnf_package, vim_instances):
        # extract information from the vnfr
        vnf_name = vnf_record.get('name')
        charm_name = vnf_name + vnf_record.get('parent_ns_id').replace('-', '')
        vnf_type = vnf_record.get('type')
        vnf_lifecycle_events = vnf_record.get('lifecycle_event')
        deploy_from_charm_store = vnf_type.startswith('juju-charm-store')

        tmp_charm_dir = None
        if not deploy_from_charm_store:
            tmp_charm_dir = self.create_charm(charm_name, vnf_lifecycle_events, vnf_package)

        # if resource allocation is done on NFVO side, take over the VMs with Juju TODO
        if str2bool(self._map.get("allocate", 'True')):
            log.debug('The NFVO will allocate resources')
            app_name_vim_machines = {}  # dict with application names as keys and vim name and machine numbers for the application
            # get ip addresses of virtual machines
            vdus = vnf_record.get('vdu')
            # group the vdus according to their vim_instances so that one can trigger the manual provisioning of machines for machines on the same vim in parallel
            vdus_by_vim = {}
            for vdu in vdus:
                used_vim = vdu.get('vimInstanceName')[0]
                if not vdus_by_vim.get(used_vim):
                    vdus_by_vim[used_vim] = [vdu]
                else:
                    vdus_by_vim.get(used_vim).append(vdu)
            time.sleep(20)  # TODO find another way to ensure that the machines are already accessible over ssh
            all_manual_provisioner_threads = []
            for vim in vdus_by_vim:
                vdus = vdus_by_vim.get(vim)
                manual_provisioner_threads_for_this_vim = []
                for vdu in vdus:
                    vnfc_instances = vdu.get('vnfc_instance')
                    for vnfc_instance in vnfc_instances:
                        floating_ip_list = vnfc_instance.get('floatingIps')
                        if floating_ip_list is None or len(floating_ip_list) == 0:
                            raise RuntimeError(
                                'Not all VNFC instances of {} have floating ips. This is a requirement for using the Juju-VNFM with resource allocation on the NFVO side.'.format(
                                    vnf_name))
                        fip = floating_ip_list[0].get('ip')
                        application_name = vnf_name + vdu.get('id').replace('-', '')
                        manual_provisioner = juju_helper.ManualProvisioner(fip, application_name)
                        manual_provisioner_threads_for_this_vim.append(manual_provisioner)
                with self.juju_command_line_semaphore:  # needed so that the newly added machines are not used by another thread
                    log.info('Calling juju switch {}'.format(vim.replace('/', ':')))
                    res = subprocess.call(['juju', 'switch', vim.replace('/', ':')])
                    log.info('Exit status: {}'.format(res))
                    for mp in manual_provisioner_threads_for_this_vim:
                        mp.start()
                    time.sleep(
                        5)  # TODO maybe there is a more elegant solution for ensuring that the juju add-machine ssh:ip commands were triggered
                    all_manual_provisioner_threads += manual_provisioner_threads_for_this_vim
            for mp in all_manual_provisioner_threads:
                mp.join()
                output = mp.output
                machine_number = None
                for line in output.splitlines():
                    if 'created machine' in line:
                        machine_number = re.findall('\d+', line)[0]
                        application_name = mp.application_name
                        if not app_name_vim_machines.get(application_name):
                            app_name_vim_machines[application_name] = {'vim': vim,
                                                                       'machines': [machine_number]}
                        else:
                            app_name_vim_machines.get(application_name).get('machines').append(
                                machine_number)
                        log.info('Added machine {}'.format(machine_number))
                if machine_number is None:
                    raise RuntimeError(
                        'Could not add the existing machine {} to Juju. This is the output: {}.'.format(fip,
                                                                                                        output))

            if deploy_from_charm_store:
                # deploy a charm from the charm store
                log.debug('Deploy from Juju Charm Store')
                series = vnf_record.get('version')
                if series not in ['precise', 'trusty', 'xenial']:
                    log.warning('{} is not a valid series for deploying a Charm. Set the VNFR\'s version to precise, '
                                'trusty or xenial.'.format(series))
                charm_name = vnf_type.split('/')[1]
                configurations = vnf_record.get('configurations')
                conf_params = []  # list of strings with the configuration parameters for the juju deploy command
                if configurations:
                    for param in configurations.get('configurationParameters'):
                        key = param.get('confKey')
                        value = param.get('value')
                        conf_params.append('  {}: {}'.format(key, value))
                for application_name in app_name_vim_machines:
                    # deploy the charm from the charm store
                    to_machine = app_name_vim_machines.get(application_name).get('machines').pop(0)
                    vim = app_name_vim_machines.get(application_name).get('vim')
                    log.debug('Deploy {} to machine {} on {}.'.format(application_name, to_machine, vim))
                    juju_requestor = juju_helper.JujuRequestor(vim)
                    with self.juju_command_line_semaphore:
                        subprocess.call(['juju', 'switch', vim.replace('/', ':')])
                        juju_requestor.deploy_from_charm_store(application_name, charm_name, 1, series=series,
                                                               conf_params=conf_params,
                                                               machine_number=to_machine)
                    log.debug('{} deployed on machine {}.'.format(charm_name, to_machine))
            else:
                # deploy the charm
                for application_name in app_name_vim_machines:
                    to_machine = app_name_vim_machines.get(application_name).get('machines').pop(0)
                    vim = app_name_vim_machines.get(application_name).get('vim')
                    log.debug('Deploy {} to machine {} on {}.'.format(application_name, to_machine, vim))
                    juju_requestor = juju_helper.JujuRequestor(vim)
                    juju_requestor.deploy_local_charm(tmp_charm_dir, application_name, 1, machine_number=to_machine)
                    log.debug('{} deployed on machine {}.'.format(charm_name, to_machine))

            # scale out until the needed number of units is reached
            for application_name in app_name_vim_machines:
                vim = app_name_vim_machines.get(application_name).get('vim')
                juju_requestor = juju_helper.JujuRequestor(vim)
                machine_numbers = app_name_vim_machines.get(application_name).get('machines')
                for to_machine in machine_numbers:
                    log.debug('Add unit to {} that will run on machine {}.'.format(application_name, to_machine))
                    juju_requestor.scale_out(application_name, machine_number=to_machine)
        else:
            log.debug('The Juju-VNFM will allocate resources')
            if deploy_from_charm_store:
                # deploy the charm from the charm store
                charm_name = vnf_type.split('/')[1]
                series = vnf_record.get('version')
                configurations = vnf_record.get('configurations')
                conf_params = []  # list of strings with the configuration parameters for the juju deploy command
                if configurations:
                    for param in configurations.get('configurationParameters'):
                        key = param.get('confKey')
                        value = param.get('value')
                        conf_params.append('  {}: {}'.format(key, value))
                with self.juju_command_line_semaphore:
                    for vdu in vnf_record.get('vdu'):
                        number_of_vnfc = len(vdu.get('vnfc'))
                        application_name = vnf_name + vdu.get('id').replace('-', '')
                        vim = vdu.get('vimInstanceName')[0]
                        subprocess.call(['juju', 'switch', vim.replace('/', ':')])
                        juju_requestor = juju_helper.JujuRequestor(vim)
                        juju_requestor.deploy_from_charm_store(application_name, charm_name, number_of_vnfc,
                                                               series=series, conf_params=conf_params)
            else:
                # deploy the charm
                for vdu in vnf_record.get('vdu'):
                    number_of_vnfc = len(vdu.get('vnfc'))
                    application_name = vnf_name + vdu.get('id').replace('-', '')
                    vim = vdu.get('vimInstanceName')[0]
                    juju_requestor = juju_helper.JujuRequestor(vim)
                    juju_requestor.deploy_local_charm(tmp_charm_dir, application_name, number_of_vnfc)

        # remove the temporary folder
        if tmp_charm_dir:
            shutil.rmtree(tmp_charm_dir)

        # wait until all the units have machine numbers assigned
        units_have_machines = False
        while not units_have_machines:
            time.sleep(1)
            units = []
            for vdu in vnf_record.get('vdu'):
                application_name = vnf_name + vdu.get('id').replace('-', '')
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_helper.JujuRequestor(vim)
                units.append(juju_requestor.get_units(application_name))
            units_have_machines = True
            for unit_object in units:
                for unit in unit_object:
                    if unit_object.get(unit).get('machine') is None or unit_object.get(unit).get('machine') == '':
                        units_have_machines = False

        wait_machines_threads = []
        for vdu in vnf_record.get('vdu'):
            application_name = vnf_name + vdu.get('id').replace('-', '')
            vim = vdu.get('vimInstanceName')[0]
            juju_requestor = juju_helper.JujuRequestor(vim)
            units = juju_requestor.get_units(application_name)
            machines = []
            for unit in units:
                log.debug('check if machines for {} are started'.format(unit))
                machines.append(units.get(unit).get('machine'))
            if len(machines) > 0:
                machine_waiter = juju_waiter.MachineWaiter(juju_requestor, machines, ['started'], ['error'])
                wait_machines_threads.append(machine_waiter)
        for t in wait_machines_threads:
            t.start()
        for t in wait_machines_threads:
            t.join()
            if not t.successful:
                log.error(t.return_message)
                raise PyVnfmSdkException(t.return_message)

        log.debug('Machines are running for ' + vnf_name)

        # inject ips and hostname in case the VNFM does resource allocation
        if not str2bool(self._map.get("allocate", 'True')):
            for vdu in vnf_record.get('vdu'):
                unit_addresses = []
                application_name = vnf_name + vdu.get('id').replace('-', '')
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_helper.JujuRequestor(vim)
                units = juju_requestor.get_units(application_name)
                for unit in units:
                    private = juju_requestor.get_private_address_from_unit(unit)
                    public = juju_requestor.get_public_address_from_unit(unit)
                    hostname = juju_requestor.get_hostname(unit)
                    log.debug('private: {}   public: {}   hostname: {}'.format(private, public, hostname))
                    if public is None:  # append unit without public address to the beginning of the list
                        [{'private': private, 'public': public, 'hostname': hostname}] + unit_addresses
                    else:  # append unit with public address to the list's end
                        unit_addresses.append({'private': private,
                                               'public': public,
                                               'hostname': hostname})
                    vnf_record.get('vnf_address').append(private)

                log.debug('unit_addresses: {}'.format(unit_addresses))
                vdu['hostname'] = vnf_record.get('name').replace('_', '-')  # TODO really necessary?
                vnfc_instances = vdu.get('vnfc_instance')
                vnfc_array = vdu.get('vnfc')
                for vnfc in vnfc_array:
                    connection_points = vnfc.get('connection_point')
                    # check if any connection point needs a floating ip
                    has_floatingIp = False
                    for connection_point in connection_points:
                        floating_ip = connection_point.get('floatingIp')
                        if floating_ip is not None:
                            has_floatingIp = True
                    if has_floatingIp:
                        unit = unit_addresses.pop()
                    else:
                        unit = unit_addresses.pop(0)

                    # create the vnfc_instance
                    # at the moment a unit can just have one network and so we have to map it to all the vnf connection points
                    vnfc_instance = {}
                    vnfc_instance['id'] = str(uuid.uuid1())
                    # TODO vnfc_instance['vim_id']
                    # TODO vnfc_instance['vc_id']
                    floating_ips = []
                    ips = []
                    vnfc_instance['connection_point'] = []
                    for connection_point in connection_points:
                        new_cp = {}
                        new_cp['id'] = str(uuid.uuid1())
                        if connection_point.get('floatingIp') is not None:
                            new_cp['floatingIp'] = unit.get('public')
                            floating_ips.append(
                                {'netName': connection_point.get('virtual_link_reference'), 'ip': unit.get('public'),
                                 'id': str(uuid.uuid1())})
                        new_cp['virtual_link_reference'] = connection_point.get('virtual_link_reference')
                        ips.append(
                            {'netName': connection_point.get('virtual_link_reference'), 'ip': unit.get('private'),
                             'id': str(uuid.uuid1())})
                    vnfc_instance['hostname'] = unit.get('hostname')
                    vnfc_instance['vnfComponent'] = vnfc
                    vnfc_instance['floatingIps'] = floating_ips
                    vnfc_instance['ips'] = ips
                    vnfc_instance['connection_point'].append(new_cp)
                    vnfc_instances.append(vnfc_instance)

        if deploy_from_charm_store:
            return vnf_record

        for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'INSTANTIATE'):
            log.debug('Trigger execution of {} on {}'.format(lifecycle_script, vnf_name))
            for vdu in vnf_record.get('vdu'):
                application_name = vnf_name + vdu.get('id').replace('-', '')
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_helper.JujuRequestor(vim)
                units = juju_requestor.get_units(application_name)
                for unit_name in units:
                    params = self.get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
                                             lifecycle_script)
                    juju_requestor.trigger_action_on_units([unit_name], 'instantiate', params=params[0])

            wait_action_threads = []
            for vdu in vnf_record.get('vdu'):
                application_name = vnf_name + vdu.get('id').replace('-', '')
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_helper.JujuRequestor(vim)
                units = juju_requestor.get_units(application_name)
                for unit_name in units:
                    action_waiter = juju_waiter.ActionWaiter(juju_requestor, unit_name, 'instantiate')
                    wait_action_threads.append(action_waiter)
            for t in wait_action_threads:
                t.start()
            for t in wait_action_threads:
                t.join()
                if not t.successful:
                    log.error(t.return_message)
                    raise PyVnfmSdkException('{} script failed'.format(lifecycle_script))
                log.debug('{} finished on {}'.format(lifecycle_script, vnf_name))
        log.info('Instantiate finished for {}'.format(vnf_name))

        return vnf_record

    def checkInstantiationFeasibility(self):
        pass

    def get_lifecycle_scripts(self, vnf_record, lifecycle_name):
        # get a list of lifecycle script names that are contained in a specific lifecycle event of a VNFR
        vnf_lifecycle_events = vnf_record.get('lifecycle_event')
        for lifecycle_event in vnf_lifecycle_events:
            if lifecycle_event.get('event') == lifecycle_name:
                return lifecycle_event.get('lifecycle_events')
        return []


def setup_logging(level=logging.INFO):
    vnfmsdk_logger = logging.getLogger('org.openbaton.python.vnfm.sdk')
    pika_logger = logging.getLogger('pika')
    jujuvnfm_logger = logging.getLogger('org.openbaton.python.vnfm.jujuvnfm')

    vnfmsdk_logger.setLevel(level)
    jujuvnfm_logger.setLevel(level)

    pika_logger.propagate = 0
    jujuvnfm_logger.propagate = 0
    vnfmsdk_logger.propagate = 0

    console_handler = logging.StreamHandler()

    simple_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(level)

    pika_logger.addHandler(console_handler)
    jujuvnfm_logger.addHandler(console_handler)
    vnfmsdk_logger.addHandler(console_handler)


def start(debug_mode=False, number_of_threads=5):
    if debug_mode:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)
    log.info("Starting the Juju-VNFM")
    start_vnfm_instances(JujuVnfm, "juju", number_of_threads)
