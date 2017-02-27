# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Microsoft Azure Machine Learning Command Line Tools.

"""

from __future__ import print_function
from builtins import input #pylint: disable=redefined-builtin
import argparse
import os
import os.path
import platform
import socket
import sys
import json
import uuid
import getopt
import time
from datetime import datetime, timedelta
import subprocess
from pkg_resources import resource_filename
from pkg_resources import resource_string
import requests
import tabulate

from azuremlcli import realtimeutilities

from azuremlcli.az_utils import az_check_components
from azuremlcli.az_utils import az_check_subscription
from azuremlcli.az_utils import az_create_resource_group
from azuremlcli.az_utils import az_login
from azuremlcli.az_utils import az_check_acs_status
from azuremlcli.az_utils import az_create_acr
from azuremlcli.az_utils import az_create_acs
from azuremlcli.az_utils import az_create_storage_account
from azuremlcli.az_utils import validate_env_name
from azuremlcli.az_utils import AzureCliError
from azuremlcli.az_utils import InvalidNameError
from azuremlcli.cli_util import InvalidConfError
from azuremlcli.cli_util import is_int
from azuremlcli.cli_util import first_run
from azuremlcli.cli_util import acs_connection_timeout
from azuremlcli.cli_util import ice_connection_timeout
from azuremlcli.cli_util import version
from azuremlcli.cli_util import CommandLineInterfaceContext

from azuremlcli.docker_utils import check_docker_credentials

from azuremlcli.realtimeutilities import check_marathon_port_forwarding
from azuremlcli.realtimeutilities import resolve_marathon_base_url
from azuremlcli.realtimeutilities import get_sample_data

from azuremlcli.batch_workflows import batch_service_create
from azuremlcli.batch_workflows import batch_service_list
from azuremlcli.batch_workflows import batch_service_view
from azuremlcli.batch_workflows import batch_service_run
from azuremlcli.batch_workflows import batch_service_delete
from azuremlcli.batch_workflows import batch_cancel_job
from azuremlcli.batch_workflows import batch_list_jobs
from azuremlcli.batch_workflows import batch_view_job

try:
    # python 3
    from urllib.request import pathname2url
    from urllib.parse import urljoin, urlparse
except ImportError:
    # python 2
    from urllib import pathname2url
    from urlparse import urljoin, urlparse

from azure.storage.blob import (BlockBlobService, ContentSettings, BlobPermissions)


def startup(context):
    """Text to print when no arguments are provided on the command line."""

    print("")
    print("")
    print("Azure Machine Learning Command Line Tools")
    print("")
    print("Base commands:")
    print("    env      : show current Azure ML related environment settings")
    print("    service  : manage Azure ML web services")
    print("")
    first_run(context)


def parse_args(context):
    """Top-level method that parses command line arguments."""

    first_run(context)
    # Just one argument provided
    if len(context.get_args()) == 2:
        if context.get_args()[1] == 'env':
            env_usage()
        elif (context.get_args()[1] == '-h') or (context.get_args()[1] == '--help') or (context.get_args()[1] == 'help'):
            startup(context)
        elif context.get_args()[1] == 'service':
            service_usage()
        elif context.get_args()[1] == '--version':
            version()
        else:
            print('Unknown base command {}. Valid commands: env, service.'.format(context.get_args()[1]))
    elif len(context.get_args()) >= 3:
        if context.get_args()[1] == 'env':
            env(context)
        elif context.get_args()[1] == 'service':
            service(context)
        else:
            print('Unknown base command {}. Valid commands: env, service.'.format(context.get_args()[1]))
    else:
        startup(context)


########################################################################################################################
#                                                                                                                      #
# Global env functions                                                                                                 #
#                                                                                                                      #
########################################################################################################################


def env(context):
    """Top level function to handle env group of commands."""

    if context.get_args()[2] == 'local':
        env_local(context, context.get_args()[3:])
    elif context.get_args()[2] == 'about':
        env_about()
    elif context.get_args()[2] == 'cluster':
        env_cluster(context, context.get_args()[3:])
    elif context.get_args()[2] == 'show':
        env_describe(context)
    elif context.get_args()[2] == 'setup':
        env_setup(context, context.get_args()[3:])
    else:
        env_usage()


def env_usage():
    """Print usage of aml env."""

    print("")
    print("Azure Machine Learning Command Line Tools")
    print("")
    print("Environment commands:")
    print("")
    print("aml env about    : learn about environment settings")
    print("aml env cluster  : switch your environment to cluster mode")
    print("aml env local    : switch your environment to local mode")
    print("aml env setup    : set up your environment")
    print("aml env show     : show current environment settings")
    print("")
    print("")


def env_describe(context):
    """Print current environment settings."""

    if context.in_local_mode():
        print("")
        print("** Warning: Running in local mode. **")
        print("To switch to cluster mode: aml env cluster")
        print("")

    print('Storage account name   : {}'.format(os.environ.get('AML_STORAGE_ACCT_NAME')))
    print('Storage account key    : {}'.format(os.environ.get('AML_STORAGE_ACCT_KEY')))
    print('ACR URL                : {}'.format(os.environ.get('AML_ACR_HOME')))
    print('ACR username           : {}'.format(os.environ.get('AML_ACR_USER')))
    print('ACR password           : {}'.format(os.environ.get('AML_ACR_PW')))

    if not context.in_local_mode():
        print('HDI cluster URL        : {}'.format(os.environ.get('AML_HDI_CLUSTER')))
        print('HDI admin user name    : {}'.format(os.environ.get('AML_HDI_USER')))
        print('HDI admin password     : {}'.format(os.environ.get('AML_HDI_PW')))
        print('ACS Master URL         : {}'.format(os.environ.get('AML_ACS_MASTER')))
        print('ACS Agent URL          : {}'.format(os.environ.get('AML_ACS_AGENT')))
        forwarded_port = check_marathon_port_forwarding(context)
        if forwarded_port > 0:
            print('ACS Port forwarding    : ON, port {}'.format(forwarded_port))
        else:
            print('ACS Port forwarding    : OFF')


def env_about():
    """Help on setting up an AML environment."""

    print("""
    Azure Machine Learning Command Line Tools

    Environment Setup
    This CLI helps you create and manage Azure Machine Learning web services. The CLI
    can be used in either local or cluster modes.


    Local mode:
    To enter local mode: aml env local

    In local mode, the CLI can be used to create locally running web services for development
    and testing. In order to run the CLI in local mode, you will need the following environment
    variables defined:

    AML_STORAGE_ACCT_NAME : Set this to an Azure storage account.
                            See https://docs.microsoft.com/en-us/azure/storage/storage-introduction for details.
    AML_STORAGE_ACCT_KEY  : Set this to either the primary or secondary key of the above storage account.
    AML_ACR_HOME          : Set this to the URL of your Azure Container Registry (ACR).
                            See https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro
                            for details.
    AML_ACR_USER          : Set this to the username of the above ACR.
    AML_ACR_PW            : Set this to the password of the above ACR.


    Cluster mode:
    To enter cluster mode: aml env cluster

    In cluster mode, the CLI can be used to deploy production web services. Realtime web services are deployed to
    an Azure Container Service (ACS) cluster, and batch web services are deployed to an HDInsight Spark cluster. In
    order to use the CLI in cluster mode, define the following environment variables (in addition to those above for
    local mode):

    AML_ACS_MASTER        : Set this to the URL of your ACS Master (e.g.yourclustermgmt.westus.cloudapp.azure.com)
    AML_ACS_AGENT         : Set this to the URL of your ACS Public Agent (e.g. yourclusteragents.westus.cloudapp.azure.com)
    AML_HDI_CLUSTER       : Set this to the URL of your HDInsight Spark cluster.
    AML_HDI_USER          : Set this to the admin user of your HDInsight Spark cluster.
    AML_HDI_PW            : Set this to the password of the admin user of your HDInsight Spark cluster.
    """)


def env_local(context, args):
    """Switches environment to local mode."""

    verbose = False
    try:
        opts, args = getopt.getopt(args, "v")
    except getopt.GetoptError:
        print("aml env local [-v]")
        return

    for opt in opts:
        if opt == '-v':
            verbose = True

    if platform.system() not in ['Linux', 'linux', 'Unix', 'unix']:
        print('Local mode is not supported on this platform.')
        return

    try:
        conf = context.read_config()
        if not conf:
            if verbose:
                print('[Debug] No configuration file found.')
            conf = {}
        elif 'mode' not in conf and verbose:
            print('[Debug] No mode setting found in config file. Suspicious.')
        conf['mode'] = 'local'
    except InvalidConfError:
        if verbose:
            print('[Debug] Suspicious content in ~/.amlconf.')
            print(conf)
            print('[Debug] Resetting.')
        conf = {'mode':'local'}

    context.write_config(conf)
    env_describe(context)
    return


def env_cluster(context, args):
    """Switches environment to cluster mode."""

    parser = argparse.ArgumentParser(prog='aml env cluster')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f',
                       action='store_true',
                       help='Force direct connection to ACS cluster.'
                      )
    group.add_argument('-p',
                       nargs='?',
                       const=None,
                       default=-1,
                       type=int,
                       help='Use port forwarding. If a port number is specified, test for an existing tunnel. Without a port number, try to set up an ssh tunnel through an unused port.' #pylint: disable=line-too-long
                      )
    parser.add_argument('-v',
                        action='store_true',
                        help='Verbose output')

    parsed_args = parser.parse_args(args)

    # if -f was specified, try direct connection only
    if parsed_args.f:
        (acs_is_setup, port) = test_acs(context, 0)
    # if only -p specified, without a port number, set up a new tunnel.
    elif not parsed_args.p:
        (acs_is_setup, port) = acs_setup(context)
    # if either no arguments specified (parsed_args.p == -1), or -p NNNNN specified (parsed_args.p == NNNNN),
    # test for an existing connection (-1), or the specified port (NNNNN)
    elif parsed_args.p:
        (acs_is_setup, port) = test_acs(context, parsed_args.p)
    # This should never happen
    else:
        (acs_is_setup, port) = (False, -1)

    if not acs_is_setup:
        continue_without_acs = input('Could not connect to ACS cluster. Continue with cluster mode anyway (y/N)? ')
        continue_without_acs = continue_without_acs.strip().lower()
        if continue_without_acs != 'y' and continue_without_acs != 'yes':
            print("Aborting switch to cluster mode. Please run 'aml env about' for more information on setting up your cluster.") #pylint: disable=line-too-long
            return

    try:
        conf = context.read_config()
        if not conf:
            conf = {}
    except InvalidConfError:
        if parsed_args.v:
            print('[Debug] Suspicious content in ~/.amlconf.')
            print(conf)
            print('[Debug] Resetting.')
        conf = {}

    conf['mode'] = 'cluster'
    conf['port'] = port
    context.write_config(conf)

    print("Running in cluster mode.")
    env_describe(context)


def env_setup(context, args):
    """
    Sets up an AML environment, including the following components:
    1. An SSH key pair, if none is found in ~/.ssh/id_rsa
    2. An ACR registry, via az cli
    3. An ACS cluster configured for that ACR registry, via az cli
    :return: Prints a set of environment variables to set and their values
    """

    parser = argparse.ArgumentParser(prog='aml env setup')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--status', metavar='deploymentId', help='Check the status of an ongoing ACS deployment.')
    group.add_argument('-n', '--name', metavar='envName',
                       help='The name of your Azure ML environment (1-20 characters, alphanumeric only).')

    parsed_args = parser.parse_args(args)

    # Check if az is installed
    try:
        az_output = subprocess.check_output(['az', '--version'], stderr=subprocess.STDOUT).decode('ascii')
    except subprocess.CalledProcessError:
        print("Couldn't find the Azure CLI installed on the system.")
        print('Please install the Azure CLI by running the following:')
        print('sudo pip install azure-cli')
        return

    if 'azure-cli' not in az_output:
        print("Couldn't find the Azure CLI installed on the system.")
        print('Please install the Azure CLI by running the following:')
        print('sudo pip install azure-cli')
        return

    # Check if the acr, acs, and storage components are installed.
    try:
        az_check_components(['acr','acs','storage'])
    except AzureCliError as exc:
        print(exc.message)
        return

    if parsed_args.name:
        try:
            validate_env_name(parsed_args.name)
        except InvalidNameError as exc:
            print('Invalid environment name. {}'.format(exc.message))
            return

    if parsed_args.status:
        try:
            (acs_master, acs_agent) = az_check_acs_status(parsed_args.status)
        except AzureCliError as exc:
            print(exc.message)
            return

        if acs_master and acs_agent:
            print('ACS deployment succeeded.')
            print('ACS Master URL     : {}'.format(acs_master))
            print('ACS Agent URL      : {}'.format(acs_agent))
            print('ACS admin username : acsadmin (Needed to set up port forwarding in cluster mode).')
            print('To configure aml with this environment, set the following environment variables.')
            if platform.system() in ['Linux', 'linux', 'Unix', 'unix']:
                print(" export AML_ACS_MASTER='{}'".format(acs_master))
                print(" export AML_ACS_AGENT='{}'".format(acs_agent))
                try:
                    with open(os.path.expanduser('~/.amlenvrc'), 'a+') as env_file:
                        env_file.write("export AML_ACS_MASTER='{}'\n".format(acs_master))
                        env_file.write("export AML_ACS_AGENT='{}'\n".format(acs_agent))
                    print('You can also find these settings saved in {}'.format(os.path.expanduser('~/.amlenvrc')))
                except IOError:
                    pass
            else:
                print(" $env:AML_ACS_MASTER = '{}'".format(acs_master))
                print(" $env:AML_ACS_AGENT = '{}'".format(acs_agent))

            print()
            print("To switch to cluster mode, run 'aml env cluster'.")

        return

    if not os.path.exists(os.path.expanduser('~/.ssh/id_rsa')):
        print('Setting up ssh key pair')
        try:
            subprocess.check_call(['ssh-keygen', '-t', 'rsa', '-b', '2048', '-f', os.path.expanduser('~/.ssh/id_rsa')])
        except subprocess.CalledProcessError:
            print('Failed to set up sh key pair. Aborting environment setup.')

    try:
        with open(os.path.expanduser('~/.ssh/id_rsa.pub'), 'r') as sshkeyfile:
            ssh_public_key = sshkeyfile.read().rstrip()
    except IOError:
        print('Could not load your SSH public key from {}'.format(os.path.expanduser('~/.ssh/id_rsa.pub')))
        print('Please run aml env setup again to create a new ssh keypair.')
        return

    print('Setting up your Azure ML environment with a storage account, ACR registry and ACS cluster.')
    if not parsed_args.name:
        root_name = input('Enter environment name (1-20 characters, lowercase alphanumeric): ')
        try:
            validate_env_name(root_name)
        except InvalidNameError as e:
            print('Invalid environment name. {}'.format(e.message))
            return
    else:
        root_name = parsed_args.name

    try:
        az_login()
        if not parsed_args.name:
            az_check_subscription()
        resource_group = az_create_resource_group(context, root_name)
        storage_account_name, storage_account_key = az_create_storage_account(context, root_name, resource_group)
    except AzureCliError as exc:
        print(exc.message)
        return

    if context.acr_home is not None and context.acr_user is not None and context.acr_pw is not None:
        print('Found existing ACR setup:')
        print('ACR Login Server: {}'.format(context.acr_home))
        print('ACR Username    : {}'.format(context.acr_user))
        print('ACR Password    : {}'.format(context.acr_pw))
        answer = input('Setup a new ACR instead (y/N)?')
        answer = answer.rstrip().lower()
        if answer != 'y' and answer != 'yes':
            print('Continuing with configured ACR.')
            acr_login_server = context.acr_home
            context.acr_username = context.acr_user
            acr_password = context.acr_pw
        else:
            (acr_login_server, context.acr_username, acr_password) = \
                az_create_acr(context, root_name, resource_group, storage_account_name)
    else:
        try:
            (acr_login_server, context.acr_username, acr_password) = \
                az_create_acr(context, root_name, resource_group, storage_account_name)
        except AzureCliError as exc:
            print(exc.message)
            return

    if context.acs_master_url is not None and context.acs_agent_url is not None:
        print('Found existing ACS setup:')
        print('ACS Master URL : {}'.format(context.acs_master_url))
        print('ACR Agent URL  : {}'.format(context.acs_agent_url))
        answer = input('Setup a new ACS instead (y/N)?')
        answer = answer.rstrip().lower()
        if answer != 'y' and answer != 'yes':
            print('Continuing with configured ACS.')
        else:
            az_create_acs(root_name, resource_group, acr_login_server, context.acr_username, acr_password, ssh_public_key)
    else:
        try:
            az_create_acs(root_name, resource_group, acr_login_server, context.acr_username, acr_password, ssh_public_key)
        except AzureCliError as exc:
            print(exc.message)

    print('To configure aml for local use with this environment, set the following environment variables.')
    if platform.system() in ['Linux', 'linux', 'Unix', 'unix']:
        print(" export AML_STORAGE_ACCT_NAME='{}'".format(storage_account_name))
        print(" export AML_STORAGE_ACCT_KEY='{}'".format(storage_account_key))
        print(" export AML_ACR_HOME='{}'".format(acr_login_server))
        print(" export AML_ACR_USER='{}'".format(context.acr_username))
        print(" export AML_ACR_PW='{}'".format(acr_password))
        try:
            with open(os.path.expanduser('~/.amlenvrc'), 'w+') as env_file:
                env_file.write("export AML_STORAGE_ACCT_NAME='{}'\n".format(storage_account_name))
                env_file.write("export AML_STORAGE_ACCT_KEY='{}'\n".format(storage_account_key))
                env_file.write("export AML_ACR_HOME='{}'\n".format(acr_login_server))
                env_file.write("export AML_ACR_USER='{}'\n".format(context.acr_username))
                env_file.write("export AML_ACR_PW='{}'\n".format(acr_password))
            print('You can also find these settings saved in {}'.format(os.path.expanduser('~/.amlenvrc')))
        except IOError:
            pass
    else:
        print(" $env:AML_STORAGE_ACCT_NAME = '{}'".format(storage_account_name))
        print(" $env:AML_STORAGE_ACCT_KEY = '{}'".format(storage_account_key))
        print(" $env:AML_ACR_HOME = '{}'".format(acr_login_server))
        print(" $env:AML_ACR_USER = '{}'".format(context.acr_username))
        print(" $env:AML_ACR_PW = '{}'".format(acr_password))

    print()


def acs_setup(context):
    """Helps set up port forwarding to an ACS cluster."""

    print('Establishing connection to ACS cluster.')
    acs_url = input('Enter ACS Master URL (default: {}): '.format(context.acs_master_url))
    if acs_url is None or acs_url == '':
        acs_url = context.acs_master_url
        if acs_url is None or acs_url == '':
            print('Error: no ACS URL provided.')
            return False, -1

    acs_username = input('Enter ACS username (default: acsadmin): ')
    if acs_username is None or acs_username == '':
        acs_username = 'acsadmin'

    # Find a random unbound port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    local_port = sock.getsockname()[1]
    print('Forwarding local port {} to port 80 on your ACS cluster'.format(local_port))
    try:
        sock.close()
        subprocess.check_call(
        ['ssh', '-L', '{}:localhost:80'.format(local_port),
         '-f', '-N', '{}@{}'.format(acs_username, acs_url), '-p', '2200'])
        return True, local_port
    except subprocess.CalledProcessError as ex:
        print('Failed to set up ssh tunnel. Error code: {}'.format(ex.returncode))
        return False, -1


def test_acs(context, existing_port):
    """

    Tests whether a valid connection to an ACS cluster exists.
    :param existing_port: If -1, check for an existing configuration setting indicating port forwarding in ~/.amlconf.
                          If 0, check for a direct connection to the ACS cluster specified in $AML_ACS_MASTER.
                          If > 0, check for port forwarding to the specified port.
    :return: (bool,int) - First value indicates whether a successful connection was made. Second value indicates the
                          port on which the connection was made. 0 indicates direct connection. Any other positive
                          integer indicates port forwarding is ON to that port.
    """
    if existing_port < 0:
        existing_port = check_marathon_port_forwarding(context)

    # port forwarding was previously setup, verify that it still works
    if existing_port > 0:
        marathon_base_url = 'http://127.0.0.1:' + str(existing_port) + '/marathon/v2'
        marathon_info_url = marathon_base_url + '/info'

        try:
            marathon_info = requests.get(marathon_info_url, timeout=acs_connection_timeout)
        except (requests.ConnectionError, requests.ConnectTimeout, requests.exceptions.ReadTimeout):
            print('Marathon endpoint not available at {}'.format(marathon_base_url))
            config_port = check_marathon_port_forwarding(context)
            if config_port == 0:
                print('Found previous direct connection to ACS cluster. Checking if it still works.')
                return test_acs(context, config_port)
            elif config_port > 0 and config_port != existing_port:
                print('Found previous port forwarding set up at {}. Checking if it still works.'.format(config_port))
                return test_acs(context, config_port)
            return acs_setup(context)
        try:
            marathon_info = marathon_info.json()
        except ValueError:
            print('Marathon endpoint not available at {}'.format(marathon_base_url))
            return acs_setup(context)
        if 'name' in marathon_info and 'version' in marathon_info and marathon_info['name'] == 'marathon':
            print('Successfully tested ACS connection. Found marathon endpoint at {}'.format(marathon_base_url))
            return (True, existing_port)
        else:
            print('Marathon endpoint not available at {}'.format(marathon_base_url))
            return acs_setup(context)

    # direct connection was previously setup, or is being requested, verify that it works
    elif existing_port == 0:
        if context.acs_master_url is not None and context.acs_master_url != '':
            marathon_base_url = 'http://' + context.acs_master_url + '/marathon/v2'
            print('Trying direct connection to ACS cluster at {}'.format(marathon_base_url))
            marathon_info_url = marathon_base_url + '/info'
            try:
                marathon_info = requests.get(marathon_info_url, timeout=acs_connection_timeout)
            except (requests.ConnectTimeout, requests.ConnectionError, requests.exceptions.ReadTimeout):
                print('Marathon endpoint not available at {}'.format(marathon_base_url))
                return (False, -1)
            try:
                marathon_info = marathon_info.json()
            except ValueError:
                print('Marathon endpoint not available at {}'.format(marathon_base_url))
                return (False, -1)
            if 'name' in marathon_info and 'version' in marathon_info and marathon_info['name'] == 'marathon':
                print('Successfully tested ACS connection. Found marathon endpoint at {}'.format(marathon_base_url))
                return (True, 0)
            else:
                print('Marathon endpoint not available at {}'.format(marathon_base_url))
                return (False, -1)
        else:
            return (False, -1)

    # No connection previously setup
    else:
        # Try ssh tunnel first
        (forwarding_set, port) = acs_setup(context)
        if not forwarding_set:
            # Try direct connection
            return test_acs(context, 0)
        else:
            return (forwarding_set, port)


########################################################################################################################
#                                                                                                                      #
# Global service functions                                                                                             #
#                                                                                                                      #
########################################################################################################################


def service(context):
    """Top level function to handle aml service group of commands."""

    if context.get_args()[2] == 'create':
        service_create(context, context.get_args()[3:])
    elif context.get_args()[2] == 'list':
        service_list(context, context.get_args()[3:])
    elif context.get_args()[2] == 'delete':
        service_delete(context, context.get_args()[3:])
    elif context.get_args()[2] == 'run':
        service_run(context, context.get_args()[3:])
    elif context.get_args()[2] == 'scale':
        service_scale(context, context.get_args()[3:])
    elif context.get_args()[2] == 'view':
        service_view(context, context.get_args()[3:])
    elif context.get_args()[2] == 'listjobs':
        service_list_jobs(context, context.get_args()[3:])
    elif context.get_args()[2] == 'viewjob':
        service_view_job(context, context.get_args()[3:])
    elif context.get_args()[2] == 'canceljob':
        service_cancel_job(context, context.get_args()[3:])
    else:
        service_usage()


def service_usage():
    """Print usage of aml service."""

    print("")
    print("")
    print("Azure Machine Learning Command Line Tools")
    print("")
    print("Service commands:")
    print("")
    print("aml service list       : list your AML web services")
    print("aml service create     : create a new AML web service")
    print("aml service run        : call an existing AML web service")
    print("aml service view       : view an existing AML web service")
    print("aml service scale      : scale an existing AML realtime web service")
    print("aml service listjobs   : list jobs of an existing AML batch web service")
    print("aml service viewjob    : view job of an existing AML batch web service")
    print("aml service canceljob  : cancel job of an existing AML batch web service")
    print("aml service delete     : delete an existing AML web service")
    print("")
    print("")


def service_list_jobs(context, args):
    """List jobs that have been run against a published service."""

    if not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service listjobs commands:")
        print("")
        print("aml service listjobs batch <options>")
        print("")
        return
    elif args[0] == 'batch':
        return batch_list_jobs(context, args[1:])
    elif args[0] == 'realtime':
        print("List jobs is not supported for realtime services.")
        return
    else:
        print("Invalid listjobs mode. Supported modes: batch")
        return


def service_view_job(context, args):
    """Show details of a specific job run against a published service."""

    if not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service viewjob commands:")
        print("")
        print("aml service viewjob batch <options>")
        print("")
        return
    elif args[0] == 'batch':
        return batch_view_job(context, args[1:])
    elif args[0] == 'realtime':
        print("View job is not supported for realtime services.")
        return
    else:
        print("Invalid viewjob mode. Supported modes: batch")
        return


def service_cancel_job(context, args):
    """Cancel an already submitted job against a published web service."""

    if not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service canceljob commands:")
        print("")
        print("aml service canceljob batch <options>")
        print("")
        return
    elif args[0] == 'batch':
        return batch_cancel_job(context, args[1:])
    elif args[0] == 'realtime':
        print("Cancel job is not supported for realtime services.")
        return
    else:
        print("Invalid canceljob mode. Supported modes: batch")


def service_create(context, args):
    """Top level function to handle creation of new web services."""

    if args is None or not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service creation commands:")
        print("")
        print("aml service create batch <options>")
        print("aml service create realtime <options>")
        print("")
        return
    elif args[0] == 'batch':
        return batch_service_create(context, args[1:])
    elif args[0] == 'realtime':
        return realtime_service_create(context, args[1:])
    else:
        print("Invalid creation mode. Supported modes: batch|realtime")
        return


def service_list(context, args):
    """List all published web services."""

    if args is None or not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service list commands:")
        print("")
        print("aml service list batch")
        print("aml service list realtime")
        print("")
        return
    elif args[0] == 'batch':
        return batch_service_list(context)
    elif args[0] == 'realtime':
        return realtime_service_list(context, args[1:])
    else:
        print('Invalid list mode. Supported modes: batch|realtime')
        return


def service_delete(context, args):
    """Delete a previously published web service."""

    if args is None or not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service delete commands:")
        print("")
        print("aml service delete batch <options>")
        print("aml service delete realtime <options>")
        print("")
        return
    elif args[0] == 'batch':
        return batch_service_delete(context, args[1:])
    elif args[0] == 'realtime':
        return realtime_service_delete(context, args[1:])
    else:
        print("Invalid deletion mode. Supported modes: batch|realtime")
        return


def service_run(context, args):
    """Run a published web service."""

    if args is None or not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service run commands:")
        print("")
        print("aml service run batch <options>")
        print("aml service run realtime <options>")
        print("")
        return
    elif args[0] == 'batch':
        return batch_service_run(context, args[1:])
    elif args[0] == 'realtime':
        return realtime_service_run(context, args[1:])
    else:
        print("Invalid creation mode. Supported modes: batch|realtime")
        return


def service_scale(context, args):
    """Scale a published web service up or down."""
    if args is None or not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service scale commands:")
        print("")
        print("aml service scale realtime -n <service_name> -c <instance_count>")
        print("")
        return
    elif args[0] == 'batch':
        print("Error: Batch services cannot be scaled.")
        return
    elif args[0] == 'realtime':
        return realtime_service_scale(context, args[1:])
    else:
        print("Invalid scale mode. Supported modes: realtime")
        return


def service_view(context, args):
    """Show details of a published web service."""

    if args is None or not args:
        print("")
        print("Azure Machine Learning Command Line Tools")
        print("")
        print("Service view commands:")
        print("")
        print("aml service view batch <options>")
        print("aml service view realtime <options>")
        print("")
        return
    elif args[0] == 'batch':
        return batch_service_view(context, args[1:])
    elif args[0] == 'realtime':
        return realtime_service_view(context, args[1:])
    else:
        print('Invalid list mode. Supported modes: batch|realtime')
        return

########################################################################################################################
#                                                                                                                      #
# Realtime service functions                                                                                           #
#                                                                                                                      #
########################################################################################################################

# Local mode functions


def realtime_service_delete_local(service_name, verbose):
    """Delete a locally published realtime web service."""

    try:
        dockerps_output = subprocess.check_output(
            ["docker", "ps", "--filter", "\"label=amlid={}\""
             .format(service_name)]).decode('ascii').rstrip().split("\n")[1:]
    except subprocess.CalledProcessError:
        print('[Local mode] Error retrieving running containers. Please ensure you have permissions to run docker.')
        return

    if dockerps_output is None or len(dockerps_output) == 0:
        print("[Local mode] Error: no service named {} running locally.".format(service_name))
        print("[Local mode] To delete a cluster based service, switch to remote mode first: aml env remote")
        return

    if len(dockerps_output) != 1:
        print("[Local mode] Error: ambiguous reference - too many containers ({}) with the same label.".format(
            len(dockerps_output)))
        return

    container_id = dockerps_output[0][0:12]
    if verbose:
        print("Killing docker container id {}".format(container_id))

    try:
        di_config = subprocess.check_output(
            ["docker", "inspect", "--format='{{json .Config}}'", container_id]).decode('ascii')
        subprocess.check_call(["docker", "kill", container_id])
        subprocess.check_call(["docker", "rm", container_id])
    except subprocess.CalledProcessError:
        print('[Local mode] Error deleting service. Please ensure you have permissions to run docker.')
        return

    try:
        config = json.loads(di_config)
    except ValueError:
        print('[Local mode] Error removing docker image. Please ensure you have permissions to run docker.')
        return

    if 'Image' in config:
        if verbose:
            print('[Debug] Removing docker image {}'.format(config['Image']))
        try:
            subprocess.check_call(["docker", "rmi", "{}".format(config['Image'])])
        except subprocess.CalledProcessError:
            print('[Local mode] Error removing docker image. Please ensure you have permissions to run docker.')
            return

    print("Service deleted.")
    return


def get_local_realtime_service_port(service_name, verbose):
    """Find the host port mapping for a locally published realtime web service."""

    try:
        dockerps_output = subprocess.check_output(
            ["docker", "ps", "--filter", "\"label=amlid={}\"".format(service_name)]).decode('ascii').rstrip().split("\n") #pylint: disable=line-too-long
    except subprocess.CalledProcessError:
        return -1
    if verbose:
        print("docker ps:")
        print(dockerps_output)
    if len(dockerps_output) == 1:
        return -1
    elif len(dockerps_output) == 2:
        container_id = dockerps_output[1][0:12]
        container_ports = subprocess.check_output(["docker", "port", container_id]).decode('ascii').strip().split('\n')
        container_ports_dict = dict(map((lambda x: tuple(filter(None, x.split('->')))), container_ports))
        # 5001 is the port we expect an ICE-built container to be listening on
        matching_ports = list(filter(lambda k: '5001' in k, container_ports_dict.keys()))
        if matching_ports is None or len(matching_ports) != 1:
            return -2
        container_port = container_ports_dict[matching_ports[0]].split(':')[1].rstrip()
        if verbose:
            print("Container port: {}".format(container_port))
        return container_port
    else:
        return -2


def realtime_service_deploy_local(context, image, verbose):
    """Deploy a realtime web service locally as a docker container."""

    print("[Local mode] Running docker container.")
    service_label = image.split("/")[1]

    # Delete any local containers with the same label
    existing_container_port = get_local_realtime_service_port(service_label, verbose)
    if is_int(existing_container_port) and int(existing_container_port) > 0:
        print('Found existing local service with the same name running at http://127.0.0.1:{}/score'
              .format(existing_container_port))
        answer = input('Delete existing service and create new service (y/N)? ')
        answer = answer.rstrip().lower()
        if answer != 'y' and answer != 'yes':
            print('Canceling service create.')
            return
        realtime_service_delete_local(service_label, verbose)

    # Check if credentials to the ACR are already configured in ~/.docker/config.json
    check_docker_credentials(context.acr_home, context.acr_user, context.acr_pw, verbose)

    try:
        docker_output = subprocess.check_output(
            ["docker", "run", "-d", "-P", "-l", "amlid={}".format(service_label), "{}".format(image)]).decode('ascii')
    except subprocess.CalledProcessError:
        print('[Local mode] Error starting docker container. Please ensure you have permissions to run docker.')
        return

    try:
        dockerps_output = subprocess.check_output(["docker", "ps"]).decode('ascii').split("\n")[1:]
    except subprocess.CalledProcessError:
        print('[Local mode] Error starting docker container. Please ensure you have permissions to run docker.')
        return

    container_created = (x for x in dockerps_output if x.startswith(docker_output[0:12])) is not None
    if container_created:
        dockerport = get_local_realtime_service_port(service_label, verbose)
        if int(dockerport) < 0:
            print('[Local mode] Failed to start container. Please report this to deployml@microsoft.com with your image id: {}'.format(image)) #pylint: disable=line-too-long
            return

        sample_data_available = get_sample_data('http://127.0.0.1:{}/sample'.format(dockerport), None, verbose)
        input_data = "'{{\"input\":\"{}\"}}'"\
            .format(sample_data_available if sample_data_available else '!! YOUR DATA HERE !!')
        print("[Local mode] Success.")
        print('[Local mode] Scoring endpoint: http://127.0.0.1:{}/score'.format(dockerport))
        print("[Local mode] Usage: aml service run realtime -n " + service_label + " [-d {}]".format(input_data))
        return
    else:
        print("[Local mode] Error creating local web service. Docker failed with:")
        print(docker_output)
        print("[Local mode] Please help us improve the product by mailing the logs to ritbhat@microsoft.com")
        return


def realtime_service_run_local(service_name, input_data, verbose):
    """Run a previously published local realtime web service."""

    container_port = get_local_realtime_service_port(service_name, verbose)
    if is_int(container_port) and int(container_port) < 0:
        print("[Local mode] No service named {} running locally.".format(service_name))
        print("To run a remote service, switch environments using: aml env remote")
        return
    else:
        headers = {'Content-Type': 'application/json'}
        if input_data == '':
            print("No input data specified. Checking for sample data.")
            sample_url = 'http://127.0.0.1:{}/sample'.format(container_port)
            sample_data = get_sample_data(sample_url, headers, verbose)
            input_data = '{{"input":"{}"}}'.format(sample_data)
            if not sample_data:
                print(
                    "No sample data available. To score with your own data, run: aml service run realtime -n {} -d <input_data>" #pylint: disable=line-too-long
                    .format(service_name))
                return
            print('Using sample data: ' + input_data)
        else:
            if verbose:
                print('[Debug] Input data is {}'.format(input_data))
                print('[Debug] Input data type is {}'.format(type(input_data)))
            try:
                json.loads(input_data)
            except ValueError:
                print('[Local mode] Invalid input. Expected data of the form \'{{"input":"[[val1,val2,...]]"}}\'')
                print('[Local mode] If running from a shell, ensure quotes are properly escaped.')
                return

        service_url = 'http://127.0.0.1:{}/score'.format(container_port)
        if verbose:
            print("Service url: {}".format(service_url))
        try:
            result = requests.post(service_url, headers=headers, data=input_data, verify=False)
        except requests.ConnectionError:
            print('[Local mode] Error connecting to container. Please try recreating your local service.')
            return

        if verbose:
            print(result.content)

        if result.status_code == 200:
            result = result.json()
            print(result['result'])
            return
        else:
            print(result.content)

# Cluster mode functions


def realtime_service_scale(context, args):
    """Scale a published realtime web service."""

    if context.in_local_mode():
        print("Error: Scaling is not supported in local mode.")
        print("To scale a cluster based service, switch to cluster mode first: aml env cluster")
        return

    service_name = ''
    instance_count = 0

    try:
        opts, args = getopt.getopt(args, "n:c:")
    except getopt.GetoptError:
        print("aml service scale realtime -n <service name> -c <instance_count>")
        return

    for opt, arg in opts:
        if opt == '-n':
            service_name = arg
        elif opt == '-c':
            instance_count = int(arg)

    if service_name == '':
        print("Error: missing service name.")
        print("aml service scale realtime -n <service name> -c <instance_count>")
        return

    if instance_count == 0 or instance_count > 5:
        print("Error: instance count must be between 1 and 5.")
        print("To delete a service, use: aml service delete")
        return

    headers = {'Content-Type': 'application/json'}
    data = {'instances': instance_count}
    marathon_base_url = resolve_marathon_base_url(context)
    if marathon_base_url is None:
        return
    marathon_url = marathon_base_url + '/marathon/v2/apps'
    success = False
    tries = 0
    print("Scaling service.", end="")
    start = time.time()
    scale_result = requests.put(marathon_url + '/' + service_name, headers=headers, data=json.dumps(data), verify=False)
    if scale_result.status_code != 200:
        print('Error scaling application.')
        print(scale_result.content)
        return

    try:
        scale_result = scale_result.json()
    except ValueError:
        print('Error scaling application.')
        print(scale_result.content)
        return

    if 'deploymentId' in scale_result:
        print("Deployment id: " + scale_result['deploymentId'])
    else:
        print('Error scaling application.')
        print(scale_result.content)
        return

    m_app = requests.get(marathon_url + '/' + service_name)
    m_app = m_app.json()
    while 'deployments' in m_app['app']:
        if not m_app['app']['deployments']:
            success = True
            break
        if int(time.time() - start) > 60:
            break
        tries += 1
        if tries % 5 == 0:
            print(".", end="")
        m_app = requests.get(marathon_url + '/' + service_name)
        m_app = m_app.json()

    print("")

    if not success:
        print("  giving up.")
        print("There may not be enough capacity in the cluster. Please try deleting or scaling down other services first.") #pylint: disable=line-too-long
        return

    print("Successfully scaled service to {} instances.".format(instance_count))
    return


def realtime_service_delete(context, args):
    """Delete a realtime web service."""

    service_name = ''
    verbose = False

    try:
        opts, args = getopt.getopt(args, "n:v")
    except getopt.GetoptError:
        print("aml service delete realtime -n <service name>")
        return

    for opt, arg in opts:
        if opt == '-n':
            service_name = arg
        elif opt == '-v':
            verbose = True

    if service_name == '':
        print("aml service delete realtime -n <service name>")
        return

    if context.in_local_mode():
        realtime_service_delete_local(service_name, verbose)
        return

    if context.acs_master_url is None:
        print("")
        print("Please set up your ACS cluster for AML. See 'aml env about' for more information.")
        return

    response = input("Permanently delete service {} (y/N)? ".format(service_name))
    response = response.rstrip().lower()
    if response != 'y' and response != 'yes':
        return

    headers = {'Content-Type': 'application/json'}
    marathon_base_url = resolve_marathon_base_url(context)
    marathon_url = marathon_base_url + '/marathon/v2/apps'
    try:
        delete_result = requests.delete(marathon_url + '/' + service_name, headers=headers, verify=False)
    except requests.ConnectTimeout:
        print('Error: timed out trying to establish a connection to ACS. Please check that your ACS is up and healthy.')
        print('For more information about setting up your environment, see: "aml env about".')
        return
    except requests.ConnectionError:
        print('Error: Could not establish a connection to ACS. Please check that your ACS is up and healthy.')
        print('For more information about setting up your environment, see: "aml env about".')
        return

    if delete_result.status_code != 200:
        print('Error deleting service: {}'.format(delete_result.content))
        return

    try:
        delete_result = delete_result.json()
    except ValueError:
        print('Error deleting service: {}'.format(delete_result.content))
        return

    if 'deploymentId' not in delete_result:
        print('Error deleting service: {}'.format(delete_result.content))
        return

    print("Deployment id: " + delete_result['deploymentId'])
    m_app = requests.get(marathon_url + '/' + service_name)
    m_app = m_app.json()
    transient_error_count = 0
    while ('app' in m_app) and ('deployments' in m_app['app']):
        if not m_app['app']['deployments']:
            break
        try:
            m_app = requests.get(marathon_url + '/' + service_name)
        except (requests.ConnectionError, requests.ConnectTimeout):
            if transient_error_count < 3:
                print('Error: lost connection to ACS cluster. Retrying...')
                continue
            else:
                print('Error: too many retries. Giving up.')
                return
        m_app = m_app.json()

    print("Deleted.")
    return


def realtime_service_create(context, args):
    """Create a new realtime web service."""

    score_file = ''
    dependencies = []
    schema_file = ''
    service_name = ''
    verbose = False
    custom_ice_url = ''

    try:
        opts, args = getopt.getopt(args, "d:f:i:m:n:s:v")
    except getopt.GetoptError:
        print("aml service create realtime -f <webservice file> -n <service name> [-m <model1> [-m <model2>] ...] [-s <schema>]") #pylint: disable=line-too-long
        return

    for opt, arg in opts:
        if opt == '-f':
            score_file = arg
        elif opt == '-m' or opt == '-d':
            dependencies.append(arg)
        elif opt == '-s':
            dependencies.append(arg)
            schema_file = arg
        elif opt == '-n':
            service_name = arg
        elif opt == '-v':
            verbose = True
        elif opt == '-i':
            custom_ice_url = arg

    if score_file == '' or service_name == '':
        print("aml service create realtime -f <webservice file> -n <service name> [-d <dependency1> [-d <dependency2>] ...]") #pylint: disable=line-too-long
        return

    storage_exists = False
    acs_exists = False
    acr_exists = False
    ice_key = None

    if context.az_account_name is None or context.az_account_key is None:
        print("")
        print("Please set up your storage account for AML:")
        print("  export AML_STORAGE_ACCT_NAME=<yourstorageaccountname>")
        print("  export AML_STORAGE_ACCT_KEY=<yourstorageaccountkey>")
        print("")
    else:
        storage_exists = True

    if (context.acs_master_url is None or context.acs_agent_url is None) and (not context.in_local_mode()):
        print("")
        print("Please set up your ACS cluster for AML:")
        print("  export AML_ACS_MASTER=<youracsmasterdomain>")
        print("  export AML_ACS_AGENT=<youracsagentdomain>")
        print("")
    else:
        acs_exists = True

    if context.acr_home is None or context.acr_user is None or context.acr_pw is None:
        print("")
        print("Please set up your ACR registry for AML:")
        print("  export AML_ACR_HOME=<youracrdomain>")
        print("  export AML_ACR_USER=<youracrusername>")
        print("  export AML_ACR_PW=<youracrpassword>")
        print("")
    else:
        acr_exists = True

    if not storage_exists or not acs_exists or not acr_exists:
        return

    # modify json payload to update assets and driver location
    payload = resource_string(__name__, 'data/testrequest.json')
    json_payload = json.loads(payload.decode('ascii'))

    # Add dependencies

    # Always inject azuremlutilities.py as a dependency from the CLI
    # It contains helper methods for serializing and deserializing schema
    utilities_filename = resource_filename(__name__, 'azuremlutilities.py')
    dependencies.append(utilities_filename)

    # If a schema file was provided, try to find the accompanying sample file
    # and add as a dependency
    sample_added = False
    get_sample_code = ''
    if schema_file is not '':
        sample_added, sample_filename = realtimeutilities.try_add_sample_file(dependencies, schema_file, verbose)
        if sample_added:
            get_sample_code = \
                resource_string(__name__, 'data/getsample.py').decode('ascii').replace('PLACEHOLDER', sample_filename)

    dependency_injection_code = '\nimport tarfile\nimport azuremlutilities\n'
    dependency_count = 0
    if dependencies is not None:
        print('Uploading dependencies.')
        for dependency in dependencies:
            (status, location, filename) = \
                realtimeutilities.upload_dependency(dependency, context.az_account_name, context.az_account_key, verbose)
            if status < 0:
                print('Error resolving dependency: no such file or directory {}'.format(dependency))
                return
            else:
                dependency_count += 1
                # Add the new asset to the payload
                new_asset = {'mimeType': 'application/octet-stream',
                             'id': str(dependency),
                             'location': location}
                json_payload['properties']['assets'].append(new_asset)
                if verbose:
                    print("Added dependency {} to assets.".format(dependency))

                # If the asset was a directory, also add code to unzip and layout directory
                if status == 1:
                    dependency_injection_code = dependency_injection_code + \
                                                'amlbdws_dependency_{} = tarfile.open("{}")\n'\
                                                .format(dependency_count, filename)
                    dependency_injection_code = dependency_injection_code + \
                                                'amlbdws_dependency_{}.extractall()\n'.format(dependency_count)

    if verbose:
        print("Code injected to unzip directories:\n{}".format(dependency_injection_code))
        print(json.dumps(json_payload))

    # read in code file
    if os.path.isfile(score_file):
        with open(score_file, 'r') as scorefile:
            code = scorefile.read()
    else:
        print("Error: No such file {}".format(score_file))
        return

    # read in fixed preamble code
    preamble = resource_string(__name__, 'data/preamble').decode('ascii')

    # wasb configuration: add the configured storage account in the as a wasb location
    wasb_config = "spark.sparkContext._jsc.hadoopConfiguration().set('fs.azure.account.key." + \
                  context.az_account_name + ".blob.core.windows.net','" + context.az_account_key + "')"

    # create blob with preamble code and user function definitions from cell
    code = "{}\n{}\n{}\n{}\n\n\n{}".format(preamble, wasb_config, dependency_injection_code, code, get_sample_code)
    if verbose:
        print(code)
    az_container_name = 'amlbdpackages'
    az_blob_name = str(uuid.uuid4()) + '.py'
    bbs = BlockBlobService(account_name=context.az_account_name,
                           account_key=context.az_account_key)
    bbs.create_container(az_container_name)
    bbs.create_blob_from_text(az_container_name, az_blob_name, code,
                              content_settings=ContentSettings(content_type='application/text'))
    blob_sas = bbs.generate_blob_shared_access_signature(
        az_container_name,
        az_blob_name,
        BlobPermissions.READ,
        datetime.utcnow() + timedelta(days=30))
    package_location = 'http://{}.blob.core.windows.net/{}/{}?{}'.format(context.az_account_name,
                                                                         az_container_name, az_blob_name, blob_sas)

    if verbose:
        print("Package uploaded to " + package_location)

    for asset in json_payload['properties']['assets']:
        if asset['id'] == 'driver_package_asset':
            if verbose:
                print("Current driver location:", str(asset['location']))
                print("Replacing with:", package_location)
            asset['location'] = package_location

    # modify json payload to set ACR credentials
    if verbose:
        print("Current ACR creds in payload:")
        print('location:', json_payload['properties']['registryInfo']['location'])
        print('user:', json_payload['properties']['registryInfo']['user'])
        print('password:', json_payload['properties']['registryInfo']['password'])

    json_payload['properties']['registryInfo']['location'] = context.acr_home
    json_payload['properties']['registryInfo']['user'] = context.acr_user
    json_payload['properties']['registryInfo']['password'] = context.acr_pw

    if verbose:
        print("New ACR creds in payload:")
        print('location:', json_payload['properties']['registryInfo']['location'])
        print('user:', json_payload['properties']['registryInfo']['user'])
        print('password:', json_payload['properties']['registryInfo']['password'])

    # call ICE with payload to create docker image

    # Set base ICE URL
    if custom_ice_url is not '':
        base_ice_url = custom_ice_url
        if base_ice_url.endswith('/'):
            base_ice_url = base_ice_url[:-1]
    else:
        base_ice_url = 'https://amlacsagent.azureml-int.net'

    create_url = base_ice_url + '/images/' + service_name
    get_url = base_ice_url + '/jobs'

    headers = {'Content-Type': 'application/json'}

    image = ''
    try:
        ice_put_result = requests.put(
            create_url, headers=headers, data=json.dumps(json_payload), timeout=ice_connection_timeout)
    except (requests.ConnectionError, requests.ConnectTimeout, requests.exceptions.ReadTimeout):
        print('Error: could not connect to Azure ML. Please try again later. If the problem persists, please contact deployml@microsoft.com') #pylint: disable=line-too-long
        return

    if ice_put_result.status_code == 401:
        print("Invalid API key. Please update your key by running 'aml env key -u'.")
        return
    elif ice_put_result.status_code != 201:
        print('Error connecting to Azure ML. Please contact deployml@microsoft.com with the stack below.')
        print(ice_put_result.content)
        return

    if verbose:
        print(ice_put_result)
    if isinstance(ice_put_result.json(), str):
        return json.dumps(ice_put_result.json())

    job_id = ice_put_result.json()['Job Id']
    if verbose:
        print('ICE URL: ' + create_url)
        print('Submitted job with id: ' + json.dumps(job_id))
    else:
        sys.stdout.write('Creating docker image.')
        sys.stdout.flush()

    job_status = requests.get(get_url + '/' + job_id, headers=headers)
    response_payload = job_status.json()
    while 'Provisioning State' in response_payload:
        job_status = requests.get(get_url + '/' + job_id, headers=headers)
        response_payload = job_status.json()
        if response_payload['Provisioning State'] == 'Running':
            time.sleep(5)
            if verbose:
                print("Provisioning image. Details: " + response_payload['Details'])
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
            continue
        else:
            if response_payload['Provisioning State'] == 'Succeeded':
                acs_payload = response_payload['ACS_PayLoad']
                acs_payload['container']['docker']['image'] = json_payload['properties']['registryInfo']['location'] \
                                                              + '/' + service_name
                image = acs_payload['container']['docker']['image']
                break
            else:
                print('Error creating image: ' + json.dumps(response_payload))
                return

    print('done.')
    print('Image available at : {}'.format(acs_payload['container']['docker']['image']))
    if context.in_local_mode():
        realtime_service_deploy_local(context, image, verbose)
        exit()
    else:
        realtime_service_deploy(context, image, service_name)
        return


def realtime_service_deploy(context, image, app_id):
    """Deploy a realtime web service from a docker image."""

    marathon_app = resource_string(__name__, 'data/marathon.json')
    marathon_app = json.loads(marathon_app.decode('ascii'))
    marathon_app['container']['docker']['image'] = image
    marathon_app['labels']['HAPROXY_0_VHOST'] = context.acs_agent_url
    marathon_app['labels']['AMLID'] = app_id
    marathon_app['id'] = app_id
    headers = {'Content-Type': 'application/json'}
    marathon_base_url = resolve_marathon_base_url(context)
    marathon_url = marathon_base_url + '/marathon/v2/apps'
    try:
        deploy_result = requests.put(
            marathon_url + '/' + app_id, headers=headers, data=json.dumps(marathon_app), verify=False)
    except requests.ConnectTimeout:
        print('Error: timed out trying to establish a connection to ACS. Please check that your ACS is up and healthy.')
        print('For more information about setting up your environment, see: "aml env about".')
        return
    except requests.ConnectionError:
        print('Error: Could not establish a connection to ACS. Please check that your ACS is up and healthy.')
        print('For more information about setting up your environment, see: "aml env about".')
        return

    if deploy_result.status_code != 200:
        print('Error creating service.')
        print(deploy_result.content)
        return

    try:
        deploy_result = deploy_result.json()
    except ValueError:
        print('Error creating service.')
        print(deploy_result.content)
        return

    print("Deployment id: " + deploy_result['deploymentId'])
    m_app = requests.get(marathon_url + '/' + app_id)
    m_app = m_app.json()
    while 'deployments' in m_app['app']:
        if not m_app['app']['deployments']:
            break
        m_app = requests.get(marathon_url + '/' + app_id)
        m_app = m_app.json()

    print("Success.")
    print("Usage: aml service run realtime -n " + app_id + " [-d '{\"input\" : \"!! YOUR DATA HERE !!\"}']")
    return


def realtime_service_view(context, args):
    """View details of a previously published realtime web service."""

    verbose = False
    pass_on_args = []

    if '-v' in args:
        verbose = True
        args = [x for x in args if x != '-v']
        pass_on_args.append('-v')

    if len(args) != 1:
        print('Usage: aml service view realtime <service_name> [-v]')
        return

    service_name = args[0]

    # First print the list view of this service
    realtime_service_list(context, pass_on_args, service_name)

    scoring_url = None
    usage_headers = ['-H "Content-Type:application/json"']
    default_sample_data = '!!!YOUR DATA HERE !!!'

    if context.in_local_mode():
        try:
            dockerps_output = subprocess.check_output(
                ["docker", "ps", "--filter", "\"label=amlid={}\"".format(service_name)])
            dockerps_output = dockerps_output.decode('ascii').rstrip().split("\n")[1:]
        except subprocess.CalledProcessError:
            print('[Local mode] Error retrieving container details. Make sure you can run docker.')
            return

        if not dockerps_output or dockerps_output is None:
            print('No such service {}.'.format(service_name))
            return

        container_id = dockerps_output[0][0:12]
        try:
            di_network = subprocess.check_output(
                ["docker", "inspect", "--format='{{json .NetworkSettings}}'", container_id]).decode('ascii')
        except subprocess.CalledProcessError:
            print('[Local mode] Error inspecting container. Make sure you can run docker.')
            return

        try:
            net_config = json.loads(di_network)
        except ValueError:
            print('[Local mode] Error retrieving container information. Make sure you can run docker.')
            return

        if 'Ports' in net_config:
            # Find the port mapped to 5001, which is where we expect our container to be listening
            scoring_port_key = [x for x in net_config['Ports'].keys() if '5001' in x]
            if len(scoring_port_key) != 1:
                print('[Local mode] Error: Malconfigured container. Cannot determine scoring port.')
                return
            scoring_port_key = scoring_port_key[0]
            scoring_port = net_config['Ports'][scoring_port_key][0]['HostPort']
            if scoring_port:
                scoring_url = 'http://127.0.0.1:' + str(scoring_port) + '/score'

            # Try to get the sample request from the container
            sample_url = 'http://127.0.0.1:' + str(scoring_port) + '/sample'
            headers = {'Content-Type':'application/json'}
        else:
            print('[Local mode] Error: Misconfigured container. Cannot determine scoring port.')
            return
    else:
        if context.acs_agent_url is not None:
            scoring_url = 'http://' + context.acs_agent_url + ':9091/score'
            sample_url = 'http://' + context.acs_agent_url + ':9091/sample'
            headers = {'Content-Type': 'application/json', 'X-Marathon-App-Id': "/{}".format(service_name)}
            usage_headers.append('-H "X-Marathon-App-Id:/{}"'.format(service_name))

    service_sample_data = get_sample_data(sample_url, headers, verbose)
    sample_data = '{{"input":"{}"}}'.format(
        service_sample_data if service_sample_data is not None else default_sample_data)
    print('Usage:')
    print('  aml  : aml service run realtime -n {} [-d \'{}\']'.format(service_name, sample_data))
    print('  curl : curl -X POST {} --data \'{}\' {}'.format(' '.join(usage_headers), sample_data, scoring_url))

    return


def realtime_service_list(context, args, service_name=None):
    """List published realtime web services."""

    verbose = False
    try:
        opts, args = getopt.getopt(args, "v")
    except getopt.GetoptError:
        print("aml service list realtime [-v]")
        return

    for opt in opts:
        if opt == '-v':
            verbose = True

    if context.in_local_mode():
        if service_name is not None:
            filter_expr = "\"label=amlid={}\"".format(service_name)
        else:
            filter_expr = "\"label=amlid\""

        try:
            dockerps_output = subprocess.check_output(
                ["docker", "ps", "--filter", filter_expr]).decode('ascii').rstrip().split("\n")[1:]
        except subprocess.CalledProcessError:
            print('[Local mode] Error retrieving running containers. Please ensure you have permissions to run docker.')
            return
        if dockerps_output is not None:
            app_table = [['NAME', 'IMAGE', 'CPU', 'MEMORY', 'STATUS', 'INSTANCES', 'HEALTH']]
            for container in dockerps_output:
                container_id = container[0:12]
                try:
                    di_config = subprocess.check_output(
                        ["docker", "inspect", "--format='{{json .Config}}'", container_id]).decode('ascii')
                    di_state = subprocess.check_output(
                        ["docker", "inspect", "--format='{{json .State}}'", container_id]).decode('ascii')
                except subprocess.CalledProcessError:
                    print('[Local mode] Error inspecting docker container. Please ensure you have permissions to run docker.') #pylint: disable=line-too-long
                    if verbose:
                        print('[Debug] Container id: {}'.format(container_id))
                    return
                try:
                    config = json.loads(di_config)
                    state = json.loads(di_state)
                except ValueError:
                    print('[Local mode] Error retrieving container details. Skipping...')
                    return

                # Name of the app
                if 'Labels' in config and 'amlid' in config['Labels']:
                    app_entry = [config['Labels']['amlid']]
                else:
                    app_entry = ['Unknown']

                # Image from the registry
                if 'Image' in config:
                    app_entry.append(config['Image'])
                else:
                    app_entry.append('Unknown')

                # CPU and Memory are currently not reported for local containers
                app_entry.append('N/A')
                app_entry.append('N/A')

                # Status
                if 'Status' in state:
                    app_entry.append(state['Status'])
                else:
                    app_entry.append('Unknown')

                # Instances is always 1 for local containers
                app_entry.append(1)

                # Health is currently not reported for local containers
                app_entry.append('N/A')
                app_table.append(app_entry)
            print(tabulate.tabulate(app_table, headers='firstrow', tablefmt='psql'))

        return

    # Cluster mode
    if service_name is not None:
        extra_filter_expr = ", AMLID=={}".format(service_name)
    else:
        extra_filter_expr = ""

    marathon_base_url = resolve_marathon_base_url(context)
    if not marathon_base_url:
        return
    marathon_url = marathon_base_url + '/marathon/v2/apps?label=AMLBD_ORIGIN' + extra_filter_expr
    if verbose:
        print(marathon_url)
    try:
        list_result = requests.get(marathon_url)
    except (requests.ConnectionError, requests.ConnectTimeout):
        print('Error connecting to ACS. Please check that your ACS cluster is up and healthy.')
        return
    try:
        apps = list_result.json()
    except ValueError:
        print('Error retrieving apps from ACS. Please check that your ACS cluster is up and healthy.')
        print(list_result.content)
        return

    if 'apps' in apps and len(apps['apps']) > 0:
        app_table = [['NAME', 'IMAGE', 'CPU', 'MEMORY', 'STATUS', 'INSTANCES', 'HEALTH']]
        for app in apps['apps']:
            if 'container' in app and 'docker' in app['container'] and 'image' in app['container']['docker']:
                app_image = app['container']['docker']['image']
            else:
                app_image = 'Unknown'
            app_entry = [app['id'].strip('/'), app_image, app['cpus'], app['mem']]
            app_instances = app['instances']
            app_tasks_running = app['tasksRunning']
            app_deployments = app['deployments']
            running = app_tasks_running > 0
            deploying = len(app_deployments) > 0
            suspended = app_instances == 0 and app_tasks_running == 0
            app_status = 'Deploying' if deploying else 'Running' if running else 'Suspended' if suspended else 'Unknown'
            app_entry.append(app_status)
            app_entry.append(app_instances)
            app_healthy_tasks = app['tasksHealthy']
            app_unhealthy_tasks = app['tasksUnhealthy']
            app_health = 'Unhealthy' if app_unhealthy_tasks > 0 else 'Healthy' if app_healthy_tasks > 0 else 'Unknown'
            app_entry.append(app_health)
            app_table.append(app_entry)
        print(tabulate.tabulate(app_table, headers='firstrow', tablefmt='psql'))
    else:
        print('No running services on your ACS cluster.')


def realtime_service_run_cluster(context, service_name, input_data, verbose):
    """Run a previously published realtime web service in an ACS cluster."""

    if context.acs_agent_url is None:
        print("")
        print("Please set up your ACS cluster for AML. Run 'aml env about' for help on setting up your environment.")
        print("")
        return

    headers = {'Content-Type': 'application/json', 'X-Marathon-App-Id': "/{}".format(service_name)}

    if input_data == '':
        sample_url = 'http://' + context.acs_agent_url + ':9091/sample'
        sample_data = get_sample_data(sample_url, headers, verbose)

        if sample_data is None:
            print('No such service {}'.format(service_name))
            return
        elif sample_data == '':
            print(
                "No sample data available. To score with your own data, run: aml service run realtime -n {} -d <input_data>" #pylint: disable=line-too-long
                .format(service_name))
            return

        input_data = '{{"input":"{}"}}'.format(sample_data)
        print('Using sample data: ' + input_data)

    marathon_url = 'http://' + context.acs_agent_url + ':9091/score'
    result = requests.post(marathon_url, headers=headers, data=input_data, verify=False)
    if verbose:
        print(result.content)

    if result.status_code != 200:
        print('Error scoring the service.')
        print(result.content)
        return

    try:
        result = result.json()
    except ValueError:
        print('Error scoring the service.')
        print(result.content)
        return

    print(result['result'])
    return


def realtime_service_run(context, args):
    """
    Execute a previously published realtime web service.
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    """

    if args is None or not args:
        print("")
        print("aml service run realtime -n <service_name> -d <input_data>")
        print("")
        return

    service_name = ''
    input_data = ''
    verbose = False

    try:
        opts, args = getopt.getopt(args, "n:d:v")
    except getopt.GetoptError:
        print("aml service run realtime -n service name -d input_data")
        return

    for opt, arg in opts:
        if opt == '-d':
            input_data = arg
        elif opt == '-n':
            service_name = arg
        elif opt == '-v':
            verbose = True

    if service_name == '':
        print("Error: missing required argument: service_name")
        print("aml service run realtime -n <service name> -d <input_data>")
        return

    if verbose:
        print("data: {}".format(input_data))

    if context.in_local_mode():
        realtime_service_run_local(service_name, input_data, verbose)
        return
    else:
        realtime_service_run_cluster(context, service_name, input_data, verbose)


########################################################################################################################
#                                                                                                                      #
# END END END Realtime service functions END END END                                                                   #
#                                                                                                                      #
########################################################################################################################

# pylint: disable=too-many-lines

if __name__ == "__main__":
    cntxt = CommandLineInterfaceContext()
    if len(cntxt.get_args()) == 1:
        startup(cntxt)
    else:
        parse_args(cntxt)
