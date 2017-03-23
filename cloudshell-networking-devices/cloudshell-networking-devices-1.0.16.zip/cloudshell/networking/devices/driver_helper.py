#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading

from cloudshell.cli.cli import CLI
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.shell.core.context_utils import get_attribute_by_name
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters, SNMPV3Parameters
from cloudshell.snmp.quali_snmp import QualiSnmp


def get_cli(session_pool_size, pool_timeout=100):
    session_pool = SessionPoolManager(max_pool_size=session_pool_size, pool_timeout=pool_timeout)
    return CLI(session_pool=session_pool)


def get_logger_with_thread_id(context):
    """
    Create QS Logger for command context AutoLoadCommandContext, ResourceCommandContext
    or ResourceRemoteCommandContext with thread name
    :param context:
    :return:
    """
    logger = LoggingSessionContext.get_logger_for_context(context)
    child = logger.getChild(threading.currentThread().name)
    for handler in logger.handlers:
        child.addHandler(handler)
    child.level = logger.level
    for log_filter in logger.filters:
        child.addFilter(log_filter)
    return child


def get_api(context):
    """

    :param context:
    :return:
    """

    return CloudShellSessionContext(context).get_api()


def get_snmp_parameters_from_command_context(command_context):
    """
    :param ResourceCommandContext command_context: command context
    :return:
    """

    snmp_version = get_attribute_by_name(context=command_context, attribute_name='SNMP Version')
    ip = command_context.resource.address

    if '3' in snmp_version:
        return SNMPV3Parameters(
            ip=ip,
            snmp_user=get_attribute_by_name(context=command_context, attribute_name='SNMP User') or '',
            snmp_password=get_attribute_by_name(context=command_context, attribute_name='SNMP Password') or '',
            snmp_private_key=get_attribute_by_name(context=command_context, attribute_name='SNMP Private Key') or ''
        )
    else:
        return SNMPV2Parameters(
            ip=ip,
            snmp_community=get_attribute_by_name(context=command_context, attribute_name='SNMP Read Community')) or ''


def get_snmp_handler(context, logger):
    snmp_handler_params = get_snmp_parameters_from_command_context(context)
    return QualiSnmp(snmp_parameters=snmp_handler_params, logger=logger)
