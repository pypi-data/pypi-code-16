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
import socket
import subprocess
import threading
import time
import traceback
import uuid
from queue import Queue, Empty

import os
import re
import shutil
import stat
import tempfile
import yaml
from vnfm.sdk.AbstractVnfmABC import AbstractVnfm, start_vnfm_instances
from vnfm.sdk.exceptions import PyVnfmSdkException
from vnfm.sdk.utils.Utilities import get_nfv_message, str2bool

import jujuvnfm.juju_helper as juju_helper
import jujuvnfm.juju_waiter as juju_waiter
from utils.utils import determine_path, raise_juju_exception

log = logging.getLogger('org.openbaton.python.vnfm.jujuvnfm.%s' % __name__)

application_names = []
available_series = ['precise', 'trusty', 'xenial']
juju_command_line_semaphore = threading.Semaphore()
deploy_store_charm_semaphore = threading.Semaphore()


def wait_conn(ip, port=22, timeout=3600):
    """
    Function for a vnf-record with only 1 ip/floating ip, waits until we can open a connection

    :param ip:
    :param port:
    :param timeout:
    :return:
    """
    sock = socket.socket()
    try:
        conn_timeout = int(timeout)
    except ValueError:
        log.debug("Could not read ssh_timeout, using default 60 seconds")
        conn_timeout = 60
    try:
        port = int(port)
    except ValueError:
        log.debug("Could not read ssh_port, using default 22")

    timeout_end = time.time() + conn_timeout

    while True:
        log.debug("Trying to reach %s at port %s" % (ip, port))
        if ip is None:
            break
        try:
            if conn_timeout:
                new_timeout = timeout_end - time.time()
                if new_timeout < 0:
                    return False
                else:
                    sock.settimeout(new_timeout)
            sock.connect((ip, port))
        except socket.timeout as err:
            if timeout:
                log.debug("SSH Timeout reached for %s on port %s" % (ip, port))
                return False
        except socket.error:
            log.debug("%s at port %s not available, trying another time" % (ip, port))
        else:
            sock.close()
            return True
        time.sleep(3)
    try:
        sock.close()
    except:
        pass
    return False


def wait_conn_thread(queue, ip, port=22, timeout=3600):
    """
    Function for a vnf-record with more then 1 ip/floating ip, waits until we can open a connection
    this function will be called by multiple threads
    :param ip:
    :param port:
    :param queue:
    :param timeout:
    :return:
    """
    sock = socket.socket()
    try:
        conn_timeout = int(timeout)
    except ValueError:
        log.debug("Could not read ssh_timeout, using default 60 seconds")
    try:
        port = int(port)
    except ValueError:
        log.debug("Could not read ssh_port, using default 22")

    if conn_timeout:
        timeout_end = time.time() + conn_timeout

    t = threading.currentThread()

    success = False
    while getattr(t, "do_run", True):
        log.debug("Trying to reach %s at port %s" % (ip, port))
        try:
            if conn_timeout:
                new_timeout = timeout_end - time.time()
                if new_timeout < 0:
                    t.do_run = False
                else:
                    sock.settimeout(new_timeout)
            if ip is None:
                t.do_run = False
            else:
                sock.connect((ip, port))
                success = True
        except socket.timeout:
            if timeout:
                log.debug("SSH Timeout reached for %s on port %s" % (ip, port))
                t.do_run = False
        except socket.error:
            log.debug("%s at port %s not available, trying another time" % (ip, port))
        else:
            sock.close()
            t.do_run = False

        time.sleep(3)
    # once finished we will return the ip, so we are able to use this function for
    # a specific number of threads , the thread finishing first will put his result
    # in a queue
    if success:
        queue.put(ip)


def check_ips_for_ssh(ips, name, ssh_port=22, ssh_timeout=3600):
    """
    Function to check a dictionary of IPs for the purpose of opening a connection,
    the function will create a thread for each ip. results will be thrown into a queue
    from which we will read.

    :param ips:
    :param name:
    :param ssh_port:
    :param ssh_timeout:
    :return:
    """
    q = Queue()
    threads = []
    # open x number of threads and take the one which responds first
    for key in ips:
        log.debug("Creating Thread for checking ssh connection on %s for %s" % (ips.get(key), name))
        t = threading.Thread(target=wait_conn_thread, args=[q, ips.get(key), ssh_port, ssh_timeout])
        t.setDaemon = True
        t.start()
        threads.append(t)
    # Block our main thread, until one result is available
    try:
        conn_ip = q.get(True, int(ssh_timeout))
        for ct in threads:
            ct.do_run = False
            ct.join
        log.debug("%s reachable by %s" % (name, conn_ip))
        # TODO kill the other threads...
        if conn_ip is not None:
            return conn_ip
        else:
            log.error("There are no IPs in the result queue for %s" % name)
            raise_juju_exception(
                'There is no reachable ip. '
                'This is a requirement for using the Juju-VNFM with resource allocation on the NFVO side.')
    except Empty:
        log.error("There are no IPs in the result queue for %s" % name)
        raise_juju_exception(
            'There is no reachable ip. '
            'This is a requirement for using the Juju-VNFM with resource allocation on the NFVO side.')


def get_params(vnfr, unit_ip_addresses, lifecycle_script, dependency=None, last_script=False):
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

    if last_script:
        params['last_script'] = 'true'
    else:
        params['last_script'] = 'false'

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


def wait_for_status(vim, app_name, expected_status=['active'], timeout=120):
    wait_time = 0
    status = juju_helper.JujuRequestor(vim).get_status(app_name)
    while status is None or status not in expected_status:
        if (wait_time * 5) >= timeout:
            raise_juju_exception("After %s seconds, %s status is not yet in active or blocked" % (
                (wait_time * 5), app_name))
        if status == 'error':
            raise_juju_exception("%s status went to error" % app_name)
        log.debug("Status of %s is still %s", app_name, status)
        wait_time += 1
        time.sleep(5)
        status = juju_helper.JujuRequestor(vim).get_status(app_name)


class JujuVnfm(AbstractVnfm):
    def __init__(self, type):
        super().__init__(type)

    def get_all_ips_for_vnf_record(self, vnf_record):
        ip_dict = {}
        for vnfc in vnf_record.get('vdu'):
            ip_dict.update(self.get_all_ips_for_vnfc(vnfc))

        return ip_dict

    def get_all_ips_for_vnfc(self, vnfc_instance):
        """
        This methods creates a dict with key netName(_floatinIp) and value ip for a vnfc_instance

        :param vnfc_instance: the vnfc_instance providing ips
        :return: a dic netName(_floatinIp): ip
        """
        ip_dict = {}
        if not vnfc_instance:
            log.error(
                "There is no vnfc_instance, using the vnfc instead, this is typically when setting the option allocate to false")
            # Check if we find the private ips, if not we for sure set the allocate option to false
        if vnfc_instance.get("ips"):
            for ip in vnfc_instance.get("ips"):
                ip_dict[ip.get("netName")] = ip.get("ip")
            for ip in vnfc_instance.get('floatingIps'):
                ip_dict[ip.get("netName") + '_floatingIp'] = ip.get("ip")

        log.debug("Found ips for vnfc_instance: %s" % ip_dict)
        return ip_dict

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
                vnfc_instance = msg.get('vnfcInstance')
                vnfr = self.scale_in(vnfr, vnfc_instance)
                log.debug("Here i return none")
                return None

            if vnfr is not None and len(vnfr) == 0:
                raise raise_juju_exception("Unknown action!")
            if nfv_message is None:
                nfv_message = get_nfv_message(action, vnfr)
            elif nfv_message == "null":
                return None
            return nfv_message
        except Exception as exception:
            log.error("Exception: %s" % exception)
            log.error("traceback is:\n%s" % traceback.format_exc())
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
            try:
                timeout = int(self._map.get("charm-status-timeout", "120"))
            except:
                timeout = 120

            for vdu in vnf_record.get('vdu'):
                application_name = self.get_app_name(vnf_name, vdu.get('id'))
                vim = vdu.get('vimInstanceName')[0]
                wait_for_status(vim, application_name, timeout=timeout)

            return vnf_record

        start_lifecycle_scripts = self.get_lifecycle_scripts(vnf_record, 'START')
        if start_lifecycle_scripts is not None and len(start_lifecycle_scripts) > 0:
            last_script = start_lifecycle_scripts[len(start_lifecycle_scripts) - 1]
        # trigger start action
        for lifecycle_script in start_lifecycle_scripts:
            log.debug('Trigger execution of {} on {}'.format(lifecycle_script, vnf_name))

            wait_action_threads = []
            for vdu in vnf_record.get('vdu'):
                application_name = self.get_app_name(vnf_name, vdu.get('id'))
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_helper.JujuRequestor(vim)
                units = juju_requestor.get_units(application_name)
                for unit_name in units:
                    if last_script == lifecycle_script:
                        params = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
                                            lifecycle_script, last_script=True)
                        log.debug("Last script is: %s" % last_script)
                    else:
                        params = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
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
                        params = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
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
            if application_name in application_names:
                application_names.remove(application_name)
            log.debug("removed application %s from %s" % (application_name, application_names))
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
        log.debug("In MODIFY method")
        log.debug("Properties are %s", self._map)

        vnf_name = vnf_record.get('name')
        deploy_from_charm_store = vnf_record.get('type').startswith('juju-charm-store')

        # for Charms from the Charm Store no modify action has to be executed
        if deploy_from_charm_store:
            vdu_ = vnf_record.get('vdu')[0]
            vim = vdu_.get('vimInstanceName')[0]
            log.debug("Using vim: %s", vim)
            juju_requestor = juju_helper.JujuRequestor(vim)

            log.info('Modify finished for {}'.format(vnf_name))
            log.debug('now running add-relation')

            target_app_name = self.get_app_name(
                vnf_record.get("type").split("/")[len(vnf_record.get("type").split("/")) - 1],
                vdu_.get('id'))

            log.debug("Target app name: %s" % target_app_name)
            relations = juju_requestor.get_relations(target_app_name)
            log.debug("Relations are: %s" % relations)
            if len(relations) != 0:
                vnfc_parameters = dependency.get("vnfcParameters")
                parameters = dependency.get("parameters")
                log.debug("vnfc_paramters object is: %s", vnfc_parameters)
                log.debug("paramters object is: %s", parameters)
                for source_type in parameters:
                    source_app_name = self.get_app_name(source_type.split("/")[len(source_type.split("/")) - 1])
                    log.debug("Source app name: %s" % source_app_name)

                    juju_source_param = []
                    juju_target_param = []
                    log.debug("looking for %s in %s", source_type, parameters)
                    for key in parameters.get(source_type).get('parameters'):
                        if "source_" in key:
                            juju_source_param.append(key.replace("source_", ""))
                        if "target_" in key:
                            juju_target_param.append(key.replace("target_", ""))

                    for index in range(len(juju_source_param)):
                        try:
                            log.debug("Triggering relation without caring of the status")
                            juju_requestor.add_relation("%s:%s" % (source_app_name, juju_source_param[index]),
                                                        "%s:%s" % (target_app_name, juju_target_param[index]))
                        except Exception as e:
                            log.error("Error while adding relation:\n\t%s" % e)
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
                application_name = self.get_app_name(vnf_name, vdu.get('id'))
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_helper.JujuRequestor(vim)
                units = juju_requestor.get_units(application_name)
                for i in range(0, number_of_executions):
                    for unit_name in units:
                        params_list = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
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

        for source in dependency.get('parameters'):
            try:
                for vdu in vnf_record.get('vdu'):
                    target = self.get_app_name(vnf_name, vdu.get('id'))
                    vim = vdu.get('vimInstanceName')[0]
                    juju_requestor = juju_helper.JujuRequestor(vim)
                    juju_requestor.add_relation("%s:%s" % (self.get_app_name(source), source),
                                                "%s:%s" % (target, 'id'))
            except:
                log.warning("not able to add fake relation")

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
        return vnf_record

    def scale_out(self, vnf_record, vnf_component, scripts, dependency):
        # get the vim on which to create the new vnfc_instance
        # vnf_component is in reality a vnfc_instance
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
            raise_juju_exception('Could not find a vim instance on which to perform the scale out')
        # extract information from the vnfr
        vnf_name = vnf_record.get('name')
        juju_requestor = juju_helper.JujuRequestor(vim_name)
        application_name = self.get_app_name(vnf_name, used_vdu.get('id'))

        # if resource allocation is done on NFVO side, take over the VMs with Juju
        if str2bool(self._map.get("allocate", 'True')):
            log.debug('NFVO have allocated resources for scale out.')
            new_vnfc_instance = None

            for vdu in vnf_record.get('vdu'):
                for vnfc_instance in vdu.get('vnfc_instance'):
                    if vnfc_instance.get('vnfComponent').get('id') == vnf_component.get('id'):
                        new_vnfc_instance = vnfc_instance

            if new_vnfc_instance is None:
                raise raise_juju_exception('Did not find a new VNFCInstance after scale out.')

            fip = self.get_fip(new_vnfc_instance, vnf_record)
            manual_provisioner = juju_helper.ManualProvisioner(fip, application_name)

            with juju_command_line_semaphore:
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
                    'Could not add the existing machine {} to Juju. This is the output: {}.'.format(fip, output))
            new_unit_name = juju_requestor.scale_out(application_name, machine_number=machine_number)
            log.info("Added new unit: %s", new_unit_name)

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
                if 'floatingIp' in connection_point and \
                        not connection_point.get('floatingIp') is None and \
                        not connection_point.get('floatingIp') == '':
                    floating_ips.append({'netName': connection_point.get('virtual_link_reference'),
                                         'ip': public})
                ips.append(({'netName': connection_point.get('virtual_link_reference'),
                             'ip': private}))

            new_vnfc_instance['floatingIps'] = floating_ips
            new_vnfc_instance['ips'] = ips
            new_vnfc_instance['id'] = str(uuid.uuid1())

            used_vdu.get('vnfc_instance').append(new_vnfc_instance)

        # TODO implement this
        if deploy_from_charm_store:
            return vnf_record

        for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'INSTANTIATE'):
            log.debug('Trigger execution of {} on {}'.format(lifecycle_script, application_name))

            params = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(new_unit_name),
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
            vnfc_parameters = dependency.get('vnfcParameters')
            source_type = lifecycle_script.split('_')[0]
            source_parameters = vnfc_parameters.get(source_type)
            if not source_parameters:
                # this lifecycle script does not start with the type of a dependency source so skip it
                continue
            number_of_executions = len(
                source_parameters.get('parameters'))  # the number of source VNFC instances for this script
            log.debug('Number of executions for {}: {}'.format(lifecycle_script, number_of_executions))
            for i in range(0, number_of_executions):
                params_list = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(new_unit_name),
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
        if vnf_component.get('state') is not None and vnf_component.get('state').lower() != "standby":
            for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'START'):
                log.debug('Trigger execution of {} on {}'.format(lifecycle_script, application_name))

                params = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(new_unit_name),
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
        """
        The vnfc_instance specifies the vnfc that should be removed.
        The vnfr specifies the vnf that should execute the SCALE_OUT event.
        """
        # get the vim on which to create the new vnfc_instance
        vim_name = None
        vnf_name = vnf_record.get('name')
        log.info("Running scale in for vnfr: %s" % vnf_name)
        log.debug("vnfc_instance to remove is: %s" % vnfc_instance)
        vnf_type = vnf_record.get('type')
        deploy_from_charm_store = vnf_type.startswith('juju-charm-store')
        if deploy_from_charm_store:
            log.warning("this scale in was never tested, use it at your own risk!")

        used_vdu = None
        for vdu in vnf_record.get('vdu'):
            log.debug("%s in %s", vnf_name, vnfc_instance.get('hostname'))
            if vnf_name in vnfc_instance.get('hostname'):
                vim_name = vdu.get('vimInstanceName')[0]
                used_vdu = vdu
                break

        if vim_name is None:
            log.info("This is a target vnfr")
            for lifecycle_script in self.get_lifecycle_scripts(vnf_record, 'SCALE_IN'):
                for vdu in vnf_record.get('vdu'):
                    application_name = self.get_app_name(vnf_name, vdu.get('id'))
                    log.debug('Trigger execution of {} on {}'.format(lifecycle_script, application_name))
                    vim_name = vdu.get('vimInstanceName')[0]
                    juju_requestor = juju_helper.JujuRequestor(vim_name)
                    unit_name = juju_requestor.get_units(application_name)[0].get('name')
                    params = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
                                        lifecycle_script)
                    juju_requestor.trigger_action_on_units([unit_name], 'scale_in', params=params[0])

                    action_waiter = juju_waiter.ActionWaiter(juju_requestor, unit_name, 'scale_in')
                    action_waiter.start()
                    action_waiter.join()
                    if not action_waiter.successful:
                        raise_juju_exception(
                            '{} script failed in START: {}'.format(lifecycle_script, action_waiter.return_message))
                    log.debug('{} finished on {}'.format(lifecycle_script, application_name))
            log.debug('Start scripts finished for {}'.format(vnf_name))
            return vnf_record
        # extract information from the vnfr

        log.debug("found vim_name %s, this is not target" % vim_name)
        application_name = self.get_app_name(vnf_name, used_vdu.get('id'))
        juju_requestor = juju_helper.JujuRequestor(vim_name)
        juju_requestor.scale_in(application_name, vnfc_instance=vnfc_instance)

        return None

    def create_charm(self, vnf_name, vnf_lifecycle_events, vnf_package, vnf_record):
        log.debug('The VNFR {} has the following lifecycle events:'.format(vnf_name))
        for lifecycle_event in vnf_lifecycle_events:
            log.debug(' * ' + lifecycle_event.get('event'))

        # create a temporary directory for the charm
        tmp_charm_dir = tempfile.mkdtemp()
        os.mkdir(tmp_charm_dir + '/actions')
        os.mkdir(tmp_charm_dir + '/scripts')
        os.mkdir(tmp_charm_dir + '/hooks')

        root_icon_path = determine_path(__file__)
        log.debug("Looking for icon in %s/etc/icon.svg" % root_icon_path)
        icon_path_ = "%s/etc/icon.svg" % determine_path(root_icon_path)
        if os.path.isfile(icon_path_):
            with open(icon_path_, "r") as icon_src:
                with open(tmp_charm_dir + '/icon.svg', 'w+') as icon_dest:
                    icon_dest.write(icon_src.read())

        with open(tmp_charm_dir + '/metadata.yaml', 'w+') as metadata_yaml:
            requires = {}
            for req in vnf_record.get('requires'):
                requires[req] = {
                    'interface': 'rel'
                }
            provides = {
                vnf_record.get('type'): {
                    'interface': 'rel'
                }
            }
            metadata = {
                'name': vnf_name,
                'description': 'Charm created by the Juju-VNFM',
                'summary': 'Charm created by the Juju-VNFM',
                'requires': requires,
                'provides': provides
            }
            metadata_yaml.write(yaml.dump(metadata))

        # add Juju action scripts and actions.yaml for the Open Baton lifecycle events
        with open(tmp_charm_dir + '/actions.yaml', 'w') as actions_yaml:
            for lifecycle_event in vnf_lifecycle_events:
                event = lifecycle_event.get('event').lower()
                with open(tmp_charm_dir + '/actions/' + event, 'w') as action:
                    action_script = '#!/bin/bash\n'
                    action_script += 'cd /opt/openbaton/scripts\n'
                    action_script += '$(action-get dependencies)\n'
                    action_script += '$(action-get configuration)\n'
                    action_script += '$(action-get outOfTheBoxParams)\n'
                    action_script += 'script=$(action-get scriptname)\n'
                    action_script += 'echo "$(date +\'%Y-%m-%d %T\') start executing $script" >> /var/log/openbaton/scriptLog\n'
                    action_script += './$script &>> /var/log/openbaton/scriptLog\n'
                    action_script += 'echo "$(date +\'%Y-%m-%d %T\') finished executing $script" >> /var/log/openbaton/scriptLog\n'
                    # if it is the last one
                    action_script += "if [ $(action-get last_script) == 'true' ]; then\n"
                    action_script += '\tstatus-set active\n'
                    action_script += 'fi\n'

                    action.write(action_script)

                    os.chmod(action.name, stat.S_IRWXU | stat.S_IXOTH)
                actions_yaml.write(
                    ('{0}:\n  description: execute the lifecycle scripts for the {0} event\n' +
                     '  params:\n    dependencies:\n      type: string\n' +
                     '    outOfTheBoxParams:\n      type: string\n' +
                     '    configuration:\n      type: string\n' +
                     '    last_script:\n      type: string\n' +
                     '    scriptname:\n      type: string\n').format(event))

        with open(tmp_charm_dir + '/hooks/start', 'w') as start_hook:
            start_hook.write(
                '#!/bin/bash\necho "started!"\nexit 0')

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
            if scripts is None:
                raise_juju_exception('There are no scripts provided in the VNFPackage for the VNF %s' % vnf_name)
            for script in scripts:
                name = script.get('name')
                payload = script.get('payload')
                content = bytearray(payload).decode('utf-8')
                if name == 'icon.svg':
                    with open(tmp_charm_dir + '/icon.svg', 'w+') as icon:
                        icon.write(content)
                        continue
                with open(tmp_charm_dir + '/scripts/{}'.format(name), 'w') as script_file:
                    script_file.write(content)
                    os.chmod(script_file.name, stat.S_IRWXU | stat.S_IXOTH)
            # add a install hook for copying the lifecycle scripts into /opt/openbaton/scripts on the deployed machine
            with open(tmp_charm_dir + '/hooks/install', 'w') as install_hook:
                install_hook.write(
                    '#!/bin/bash\n'
                    'mkdir -p /var/log/openbaton\n'
                    'mkdir -p /opt/openbaton\n'
                    'mv scripts /opt/openbaton/scripts\n'
                    'chmod -R +x /opt/openbaton/scripts/*'
                )
            log.debug('Scripts are provided by the VNFPackage')

        return tmp_charm_dir

    def instantiate(self, vnf_record, vnf_package, vim_instances):

        # extract information from the vnfr
        vnf_name = vnf_record.get('name')
        vnf_type = vnf_record.get('type')
        for vdu in vnf_record.get('vdu'):
            charm_name = self.get_app_name(vnf_name, vdu.get('id'))
        vnf_lifecycle_events = vnf_record.get('lifecycle_event')
        deploy_from_charm_store = vnf_type.startswith('juju-charm-store')
        tmp_charm_dir = None
        if not deploy_from_charm_store:
            tmp_charm_dir = self.create_charm(charm_name, vnf_lifecycle_events, vnf_package, vnf_record)

        # if resource allocation is done on NFVO side, take over the VMs with Juju TODO
        if str2bool(self._map.get("allocate", 'True')):
            log.info('The NFVO has already allocated resources')

            # dict with application names as keys and vim name and machine numbers for the application
            app_name_vim_machines = {}

            ########################################
            # get ip addresses of virtual machines #
            ########################################

            vdus = vnf_record.get('vdu')

            # group the vdus according to their vim_instances so that one can trigger
            # the manual provisioning of machines for machines on the same vim in parallel
            vdus_by_vim = {}
            for vdu in vdus:
                used_vim = vdu.get('vimInstanceName')[0]
                if not vdus_by_vim.get(used_vim):
                    vdus_by_vim[used_vim] = [vdu]
                else:
                    vdus_by_vim.get(used_vim).append(vdu)

            all_manual_provisioner_threads = []

            for vim in vdus_by_vim:
                vdus = vdus_by_vim.get(vim)
                manual_provisioner_threads_for_this_vim = []

                for vdu in vdus:
                    vnfc_instances = vdu.get('vnfc_instance')
                    for vnfc_instance in vnfc_instances:
                        # check which of the floatingIPs or general ips is available is already done before..
                        log.debug("Starting threads to get the right floating ip")
                        fip = self.get_fip(vnfc_instance=vnfc_instance, vnf_record=vnf_record)
                        application_name = self.get_app_name(vnf_name, vdu.get('id'))
                        manual_provisioner = juju_helper.ManualProvisioner(fip, application_name)
                        manual_provisioner_threads_for_this_vim.append(manual_provisioner)

                # needed so that the newly added machines are not used by another thread
                log.debug("before semaphore acquire")
                log.debug("Semaphore is available? %s" % juju_command_line_semaphore)
                with juju_command_line_semaphore:
                    log.info('Calling juju switch {}'.format(vim.replace('/', ':')))
                    res = subprocess.call(['juju', 'switch', vim.replace('/', ':')])
                    log.info('Exit status: {}'.format(res))
                    for mp in manual_provisioner_threads_for_this_vim:
                        mp.start()
                    # TODO maybe there is a more elegant solution for ensuring that the juju add-machine ssh:ip commands were triggered
                    time.sleep(5)
                    all_manual_provisioner_threads += manual_provisioner_threads_for_this_vim
                log.debug("released Semaphore")
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
                charm_name = "/".join(vnf_type.split('/')[1:])
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
                    with juju_command_line_semaphore:
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
                    series = 'trusty'
                    if vnf_record.get('version') in available_series:
                        series = vnf_record.get('version')
                    juju_requestor.deploy_local_charm(tmp_charm_dir, application_name, 1, machine_number=to_machine,
                                                      series=series)
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
            log.info('The Juju-VNFM will allocate resources')
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
                with juju_command_line_semaphore:
                    for vdu in vnf_record.get('vdu'):
                        number_of_vnfc = len(vdu.get('vnfc'))
                        application_name = self.get_app_name(vnf_name, vdu.get('id'))
                        vim = vdu.get('vimInstanceName')[0]
                        subprocess.call(['juju', 'switch', vim.replace('/', ':')])
                        juju_requestor = juju_helper.JujuRequestor(vim)
                        juju_requestor.deploy_from_charm_store(application_name, charm_name, number_of_vnfc,
                                                               series=series, conf_params=conf_params)
            else:
                # deploy the charm
                for vdu in vnf_record.get('vdu'):
                    number_of_vnfc = len(vdu.get('vnfc'))
                    application_name = self.get_app_name(vnf_name, vdu.get('id'))
                    vim = vdu.get('vimInstanceName')[0]
                    juju_requestor = juju_helper.JujuRequestor(vim)
                    series = 'trusty'
                    if vnf_record.get('version') in available_series:
                        series = vnf_record.get('version')
                    juju_requestor.deploy_local_charm(tmp_charm_dir, application_name, number_of_vnfc, series=series)

        # remove the temporary folder
        if tmp_charm_dir:
            shutil.rmtree(tmp_charm_dir)

        # wait until all the units have machine numbers assigned
        units_have_machines = False
        while not units_have_machines:
            time.sleep(1)
            units = []
            for vdu in vnf_record.get('vdu'):
                application_name = self.get_app_name(vnf_name, vdu.get('id'))
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
            application_name = self.get_app_name(vnf_name, vdu.get('id'))
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
                application_name = self.get_app_name(vnf_name, vdu.get('id'))
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
                    has_floating_ip = False
                    for connection_point in connection_points:
                        floating_ip = connection_point.get('floatingIp')
                        if floating_ip is not None:
                            has_floating_ip = True
                    if has_floating_ip:
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
            juju_requestors_per_vim = {}
            for vdu in vnf_record.get('vdu'):
                application_name = self.get_app_name(vnf_name, vdu.get('id'))
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_requestors_per_vim.get(vim)
                if juju_requestor is None:
                    juju_requestor = juju_helper.JujuRequestor(vim)
                    juju_requestors_per_vim[vim] = juju_requestor
                units = juju_requestor.get_units(application_name)
                for unit_name in units:
                    params = get_params(vnf_record, juju_requestor.get_ip_addresses_from_unit(unit_name),
                                        lifecycle_script)
                    juju_requestor.trigger_action_on_units([unit_name], 'instantiate', params=params[0])
                    log.debug("All actions now: %s" % juju_requestor.get_completed_actions([unit_name]))

            wait_action_threads = []
            for vdu in vnf_record.get('vdu'):
                application_name = self.get_app_name(vnf_name, vdu.get('id'))
                vim = vdu.get('vimInstanceName')[0]
                juju_requestor = juju_requestors_per_vim.get(vim)
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
                log.debug("Output of the script %s:\n%s" % (lifecycle_script, t.return_message))
        log.info('Instantiate finished for {}'.format(vnf_name))

        return vnf_record

    def get_app_name(self, vnf_name, id=None):
        if id is not None:
            result = vnf_name + id.replace('-', '')
            if result not in application_names and "/" not in result:
                application_names.append(result)
            return result
        else:
            log.debug("Appnames: %s", application_names)
            for name in application_names:
                if vnf_name in name:
                    log.warning("Guessing the appname!")
                    if "/" in name:
                        name = name.split("/")[len(name.split("/")) - 1]
                    return name

    def checkInstantiationFeasibility(self):
        pass

    def get_lifecycle_scripts(self, vnf_record, lifecycle_name):
        # get a list of lifecycle script names that are contained in a specific lifecycle event of a VNFR
        vnf_lifecycle_events = vnf_record.get('lifecycle_event')
        for lifecycle_event in vnf_lifecycle_events:
            if lifecycle_event.get('event') == lifecycle_name:
                return lifecycle_event.get('lifecycle_events')
        return []

    def get_fip(self, vnfc_instance, vnf_record):
        # Found another way to ensure that the machines are already accessible over ssh
        ################################################
        # Assemble all available IPs in one dictionary #
        ################################################
        ip_dict = self.get_all_ips_for_vnfc(vnfc_instance)

        # Check which of the IPs is acutally reachable
        vnf_name = vnf_record.get('name')
        if len(ip_dict) > 1:
            fip = check_ips_for_ssh(ip_dict, vnf_name)
            log.debug("Found fip: %s" % fip)
            return fip

        # If we only have 1 ip we can just use the actual value of the internal ip
        elif len(ip_dict) == 1:
            if not wait_conn(ip_dict.items()[0]):
                # If there is no reachable IP , we raise an error
                raise RuntimeError(
                    'Not all VNFC instances of {} have a reachable ip. '
                    'This is a requirement for using the Juju-VNFM with resource allocation on the NFVO side.'
                        .format(vnf_name))
            log.debug("Found fip: %s" % ip_dict.items()[0])
            return ip_dict.items()[0]


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

    simple_formatter = logging.Formatter('%(asctime)s - %(name)s - line:%(lineno)d - %(levelname)s - %(message)s')

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
