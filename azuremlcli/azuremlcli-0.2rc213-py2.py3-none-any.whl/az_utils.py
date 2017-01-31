# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Utilities to interact with the Azure CLI (az).

"""


import datetime
import json
import re
import subprocess
import uuid
from pkg_resources import resource_filename
from pkg_resources import resource_string

from azuremlcli.cli_util import aml_env_default_location


# EXCEPTIONS
class Error(Exception):
    """Base class for exceptions raised by this file."""
    pass


class AzureCliError(Error):
    """Exception raised when an Azure CLI operation fails."""

    def __init__(self, message):
        super().__init__()
        self.message = message


def az_login():
    """Log in to Azure if not already logged in"""

    try:
        subprocess.check_call(['az', 'account', 'show'])
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call(['az', 'login'])
        except subprocess.CalledProcessError:
            raise AzureCliError('Error logging in to Azure. Please try again later.')


def az_check_subscription():
    """Check whether the user wants to use the current default subscription"""

    try:
        az_account_result = subprocess.check_output(['az', 'account', 'show']).decode('ascii')
        az_account_result = json.loads(az_account_result)
    except (subprocess.CalledProcessError, ValueError):
        raise AzureCliError(
            'Error retrieving subscription information from Azure. Please try again later.')

    if 'name' in az_account_result:
        current_subscription = az_account_result['name']
        print('Subscription set to {}'.format(current_subscription))
        answer = input('Continue with this subscription (Y/n)? ')
        answer = answer.rstrip().lower()
        if answer == 'n' or answer == 'no':
            new_subscription = input('Enter subscription name: ')
            new_subscription = new_subscription.rstrip()
            try:
                subprocess.check_call(['az', 'account', 'set', '--subscription', new_subscription])
            except subprocess.CalledProcessError:
                raise AzureCliError('Invalid subscription.')
    else:
        raise AzureCliError(
            'Error retrieving subscription information from Azure. Please try again later.')


def az_create_resource_group(root_name):
    """Create a resource group using root_name as a prefix"""

    rg_name = root_name + 'rg'
    try:
        rg_exists = subprocess.check_output(['az', 'group', 'exists', '-n', rg_name])
        rg_exists = rg_exists.decode('ascii').rstrip()
    except subprocess.CalledProcessError:
        # If the check fails for some reason, try to create anyway
        pass

    if not rg_exists or (rg_exists and rg_exists != 'true'):
        print('Creating resource group {}.'.format(rg_name))
        try:
            output = subprocess.check_output(
                ['az', 'group', 'create', '-l', aml_env_default_location, '-n', rg_name])
        except subprocess.CalledProcessError as exc:
            if output and 'already exists' not in output:
                raise AzureCliError(
                    'Unable to create a resource group. Please try again later. Error code: {}'
                    .format(exc.returncode))
    else:
        print('Resource group {} already exists, skipping creation.'.format(rg_name))

    return rg_name


def az_register_provider(namespace):
    """ Registers a given resource provider with Azure."""
    try:
        subprocess.check_call(
            ['az', 'provider', 'register', '-n', namespace], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        raise AzureCliError(
            'Failed to register provider {}. Error details: {}'
            .format(namespace, exc.output.decode('ascii')))

    registered = False

    while not registered:
        try:
            show_output = subprocess.check_output(
                ['az', 'provider', 'show', '-n', namespace], stderr=subprocess.STDOUT)
            show_output = show_output.decode('ascii')
        except subprocess.CalledProcessError as exc:
            raise AzureCliError(
                'Failed to get registration state for provider {}. Error details: {}'
                .format(namespace, exc.output.decode('ascii')))

        try:
            show_output = json.loads(show_output)
        except ValueError:
            raise AzureCliError(
                'Malformed response when getting registration state. Please report to azureml@microsoft.com with this output: {}' #pylint: disable=line-too-long
                .format(show_output))

        if 'registrationState' not in show_output:
            raise AzureCliError(
                'Malformed response when getting registration state. Please report to azureml@microsoft.com with this output: {}' #pylint: disable=line-too-long
                .format(json.dumps(show_output)))

        if show_output['registrationState'] == 'Registered':
            registered = True

    return registered


def az_create_storage_account(root_name, resource_group, salt=None):
    """
    Create a storage account for the AML environment.
    :param root_name: The name to use as a prefix for the storage account.
    :param resource_group: The resource group in which to create the storage account.
    :param salt: An optional salt to append to the storage account name.
    :return: string - the name of the storage account created, if successful.
    """

    storage_account_name = root_name + 'storage'
    if salt:
        storage_account_name = storage_account_name + salt

    az_register_provider('Microsoft.Storage')
    try:
        print('Creating storage account {}.'.format(storage_account_name))
        storage_create_output = subprocess.check_output(
            ['az', 'storage', 'account', 'create', '-g', resource_group, '-l', aml_env_default_location, '-n',
             storage_account_name, '--sku', 'Standard_LRS'], stderr=subprocess.STDOUT).decode('ascii')
    except subprocess.CalledProcessError as exc:
        if 'already taken' in exc.output.decode('ascii'):
            print('A storage account named {} already exists.'.format(storage_account_name))
            salt = str(uuid.uuid4())[:6]
            return az_create_storage_account(root_name, resource_group, salt)
        else:
            raise AzureCliError(
                'Error creating storage account. Please report this to azureml@microsoft.com with the following output: {}' #pylint: disable=line-too-long
                .format(exc.output))

    try:
        storage_create_output = json.loads(storage_create_output)
        if 'provisioningState' in storage_create_output and storage_create_output['provisioningState'] == 'Succeeded':
            try:
                storage_account_keys = subprocess.check_output(
                    ['az', 'storage', 'account', 'keys', 'list', '-n', storage_account_name, '-g', resource_group],
                    stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as exc:
                raise AzureCliError('Error retrieving storage account keys: {}'.format(exc.output))

            try:
                storage_account_keys = json.loads(storage_account_keys.decode('ascii'))
            except ValueError:
                raise AzureCliError('Error retrieving storage account keys: {}'.format(storage_account_keys))

            if 'keys' not in storage_account_keys or len(storage_account_keys['keys']) != 2:
                raise AzureCliError(
                    'Error retrieving storage account keys: {}'.format(json.dumps(storage_account_keys)))

            if 'keyName' not in storage_account_keys['keys'][1] or 'value' not in storage_account_keys['keys'][1]:
                raise AzureCliError(
                    'Error retrieving storage account keys: {}'.format(json.dumps(storage_account_keys)))

            return storage_account_name, storage_account_keys['keys'][1]['value']
        else:
            raise AzureCliError(
                'Malformed response while creating storage account. Please report this to azureml@microsoft.com with the following output: {}' #pylint: disable=line-too-long
                .format(json.dumps(storage_create_output)))
    except ValueError:
        raise AzureCliError(
            'Malformed response while creating storage account. Please report this to azureml@microsoft.com with the following output: {}' #pylint: disable=line-too-long
            .format(json.dumps(storage_create_output)))


def az_create_acr(root_name, resource_group, storage_account_name):
    """
    Create an ACR registry using the Azure CLI (az).
    :param root_name: The prefix to attach to the ACR name.
    :param resource_group: The resource group in which to create the ACR.
    :param storage_account_name: The storage account to use for the ACR.
    :return: Tuple - the ACR login server, username, and password
    """

    az_register_provider('Microsoft.ContainerRegistry')
    acr_name = root_name + 'acr'
    print('Creating ACR registry: {} (please be patient, this can take several minutes)'.format(acr_name))
    try:
        acr_create = subprocess.Popen(
            ['az', 'acr', 'create', '-n', acr_name, '-l', aml_env_default_location, '-g', resource_group,
             '--storage-account-name', storage_account_name, '--admin-enabled', 'true'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = acr_create.communicate()
        if err:
            result = err.decode('ascii')
            if 'already in use' in result:
                try:
                    existing_acr_details = subprocess.check_output(['az', 'acr', 'show', '-n', acr_name],
                                                                   stderr=subprocess.STDOUT).decode('ascii')
                except subprocess.CalledProcessError as exc2:
                    raise AzureCliError('ACR already exists, but failed to retrieve metadata. Error: {}'.format(
                        exc2.output.decode('ascii')))
                try:
                    existing_acr_details = json.loads(existing_acr_details)
                    if 'loginServer' not in existing_acr_details:
                        raise AzureCliError(
                            'ACR already exists, but metadata was malformed. Metadata received: {}'.format(
                                json.dumps(existing_acr_details)))
                    print('Found existing ACR named {}.'.format(acr_name))
                    acr_login_server = existing_acr_details['loginServer']
                except ValueError:
                    raise AzureCliError('ACR already exists, but metadata was malformed. Metadata received: {}'.format(
                        existing_acr_details))
            else:
                try:
                    acr_create_result = json.loads(output.decode('ascii'))
                    if 'loginServer' not in acr_create_result:
                        raise AzureCliError(
                            'ACR metadata was malformed. Metadata received: {}'.format(json.dumps(acr_create_result)))
                    acr_login_server = acr_create_result['loginServer']
                except ValueError:
                    raise AzureCliError(
                        'Error creating ACR. Please try again later. Response from az was not json: {}.'.format(
                            acr_create_result))
    except Exception as exc:
        raise AzureCliError(
            'Error creating ACR. Please try again later. Error: {}'.format(exc.output.decode('ascii')))

    try:
        acr_credentials = subprocess.check_output(['az', 'acr', 'credential', 'show', '-n', acr_name])
    except subprocess.CalledProcessError:
        raise AzureCliError('Error retrieving ACR credentials. ')

    try:
        acr_credentials = json.loads(acr_credentials.decode('ascii'))
    except ValueError:
        raise AzureCliError('Error retrieving ACR credentials. Please try again later.')

    acr_username = acr_credentials['username']
    acr_password = acr_credentials['password']

    return acr_login_server, acr_username, acr_password


def az_create_acs(root_name, resource_group, acr_login_server, acr_username, acr_password, ssh_public_key):
    """
    Creates an ACS cluster using the Azure CLI and our ARM template. This function should only
    be called after create_acr above. It assumes that the user is already logged in to Azure, and
    that the Azure CLI (az) is present on the system.
    :param root_name: The prefix of the ACS master and agent DNS names.
    :param resource_group: The resource group in which to create the ACS.
    :param acr_login_server: The URL to the ACR that will be connected to this ACS.
    :param acr_username: The username of the ACR connected to this ACS.
    :param acr_password: The password for the above user of ACR.
    :param ssh_public_key: The AML CLI user's public key that will be configured on the masters and agents of this ACS.
    :return: A tuple of DNS names for the ACS master and agent.
    """

    # Load the parameters file
    template_file = resource_filename(__name__, 'data/acstemplate.json')
    parameters = json.loads(resource_string(__name__, 'data/acstemplateparameters.json').decode('ascii'))
    deployment_name = resource_group + 'acsdeployment' + datetime.datetime.now().strftime('%Y%m%d%I%M%S')
    acs_master_prefix = root_name + 'acsmaster'
    acs_agent_prefix = root_name + 'acsagent'
    parameters['masterEndpointDNSNamePrefix']['value'] = acs_master_prefix
    parameters['agentpublicEndpointDNSNamePrefix']['value'] = acs_agent_prefix
    parameters['sshRSAPublicKey']['value'] = ssh_public_key
    parameters['azureContainerRegistryName']['value'] = acr_login_server
    parameters['azureContainerRegistryUsername']['value'] = acr_username
    parameters['azureContainerRegistryPassword']['value'] = acr_password

    try:
        subprocess.check_output(
            ['az', 'group', 'deployment', 'create', '-g', resource_group, '-n', deployment_name, '--template-file',
             template_file, '--parameters', json.dumps(parameters), '--no-wait'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        if exc.output:
            result = exc.output.decode('ascii')
            if 'is not valid according' in result:
                print(
                    'ACS provisioning via template failed. This might mean you do not have enough resources in your subscription.') #pylint: disable=line-too-long
                if 'tracking id' in result:
                    tracking_id = re.search("tracking id is '(.+)'", result).group(1)
                    print('The tracking id is {}.'.format(tracking_id))
                    print('You can login to https://portal.azure.com to find more details about this error.')

        raise AzureCliError('Error creating ACS from template. Error details {}'.format(exc.output.decode('ascii')))

    print('Started ACS deployment. Please note that it can take up to 15 minutes to complete the deployment.')
    print('You can continue to work with aml in local mode while the ACS is being provisioned.')
    print("To check the status of the deployment, run 'aml env setup -s {}'".format(deployment_name))


def az_check_acs_status(deployment_name):
    """
    Check the status of a previously started ACS deployment.
    :param deployment_name: The name of the deployment.
    :return: If deployment succeeded, return the master and agent URLs. If not, display the deployment status.
    """

    # Log in to Azure if not already logged in
    az_login()

    if 'acsdeployment' not in deployment_name:
        raise AzureCliError('Not a valid AML deployment name.')

    resource_group = deployment_name.split('acsdeployment')[0]
    try:
        acs_status = subprocess.check_output(
            ['az', 'group', 'deployment', 'show', '-g', resource_group, '-n', deployment_name],
            stderr=subprocess.STDOUT).decode('ascii')
    except subprocess.CalledProcessError as exc:
        raise AzureCliError('Error retrieving deployment status: {}'.format(exc.output.decode('ascii')))

    try:
        acs_status = json.loads(acs_status)
    except ValueError:
        raise AzureCliError(
            'Malformed deployment status. Please report this to azureml@microsoft.com, with the following in your error report: {}' #pylint: disable=line-too-long
            .format(acs_status))

    if 'properties' not in acs_status or 'provisioningState' not in acs_status['properties']:
        raise AzureCliError(
            'Error retrieving deployment status. Returned object from az cli: {}'.format(json.dumps(acs_status)))

    if acs_status['properties']['provisioningState'] != 'Succeeded':
        print('Deployment status: {}'.format(acs_status['properties']['provisioningState']))
        return None, None

    if 'outputs' not in acs_status['properties']:
        raise AzureCliError(
            'No outputs in deployment. Please report this to azureml@microsoft.com, with the following json in your error report: {}' #pylint: disable=line-too-long
            .format(json.dumps(acs_status)))

    if 'agentpublicFQDN' not in acs_status['properties']['outputs'] \
            or 'masterFQDN' not in acs_status['properties']['outputs']:
        raise AzureCliError(
            'Malformed output in deployment. Please report this to azureml@microsoft.com, with the following json in your error report: {}' #pylint: disable=line-too-long
            .format(json.dumps(acs_status)))

    return acs_status['properties']['outputs']['masterFQDN']['value'], \
           acs_status['properties']['outputs']['agentpublicFQDN']['value']
