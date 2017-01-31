# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
batch_cli_util.py - Defines utilities, constants for batch portion of azureml CLI
"""

from __future__ import print_function
import os
from collections import OrderedDict
import requests
from azuremlcli.cli_util import get_json
from azuremlcli.cli_util import az_account_name
from azuremlcli.cli_util import az_account_key
from azuremlcli.cli_util import in_local_mode
from azuremlcli.cli_util import hdi_domain
from azuremlcli.cli_util import hdi_user
from azuremlcli.cli_util import hdi_pw
from azuremlcli.cli_util import get_success_and_resp_str
from azuremlcli.cli_util import ValueFunction
from azuremlcli.cli_util import TraversalFunction
from azuremlcli.cli_util import ConditionalListTraversalFunction

# CONSTANTS
BATCH_URL_BASE_FMT = 'https://{}-aml.apps.azurehdinsight.net' if not in_local_mode() \
    else 'http://localhost:8080'
BATCH_HEALTH_FMT = '{}/v1/health'.format(BATCH_URL_BASE_FMT)
BATCH_DEPLOYMENT_INFO_FMT = '{}/v1/deploymentinfo'.format(BATCH_URL_BASE_FMT)
BATCH_ALL_WS_FMT = '{}/v1/webservices'.format(BATCH_URL_BASE_FMT)
BATCH_SINGLE_WS_FMT = '{}/{{}}'.format(BATCH_ALL_WS_FMT)
BATCH_ALL_JOBS_FMT = '{}/jobs'.format(BATCH_SINGLE_WS_FMT)
BATCH_SINGLE_JOB_FMT = '{}/{{}}'.format(BATCH_ALL_JOBS_FMT)
BATCH_CANCEL_JOB_FMT = '{}/cancel'.format(BATCH_SINGLE_JOB_FMT)

BATCH_EXTENSION_TO_ASSET_DICT = {'.py': 'PythonAssets',
                                 '.jar': 'JarAssets'}


# EXCEPTION CLASSES
class InvalidStorageException(Exception):
    """
    Exception raised when determining valid storage fails
    """


# UTILITY FUNCTIONS
def batch_get_url(fmt, *args):
    """
    function to construct target url depending on whether in local mode or not
    :param fmt: str format string to build url from
    :param args: list arguments to populate format string with
    :return:
    """
    url = fmt.format(*args[1:]) if in_local_mode() else fmt.format(*args)
    return url


def batch_get_asset_type(asset_id):
    """

    :param asset_id: str id of asset, expected form <name>.<extension>
    :return: str type of resource the asset's extension indicates
    """
    extension = os.path.splitext(asset_id)[1]
    if extension in BATCH_EXTENSION_TO_ASSET_DICT:
        return BATCH_EXTENSION_TO_ASSET_DICT[extension]

    return 'FileAssets'


def batch_get_parameter_str(param_dict):
    """

    :param param_dict: dictionary of Parameter descriptions
    :return: formatted string for Usage associated with this parameter
    """
    letter = '-o' if param_dict['Direction'] == 'Output' else \
        ('-i' if param_dict['Kind'] == 'Reference' else '-p')
    ret_val = '{} {}=<value>'.format(letter, param_dict['Id'])
    return '[{}]'.format(ret_val) if 'Value' in param_dict else ret_val


def batch_get_job_description(http_content):
    """

    :param http_content: requests.content object with json encoded job
    :return: str value to print as job description
    """
    json_obj = get_json(http_content)
    return_str = 'Name: {}\n'.format(json_obj['WebServiceId'])
    return_str += 'JobId: {}\n'.format(json_obj['JobId'])
    if 'YarnAppId' in json_obj:
        return_str += 'YarnAppId: {}\n'.format(json_obj['YarnAppId'])
        return_str += 'Logs available at: https://{}.azurehdinsight.net/' \
                      'yarnui/hn/cluster/app/{}\n'.format(hdi_domain, json_obj['YarnAppId'])
    elif 'DriverLogFile' in json_obj:
        return_str += 'Logs available at: {}\n'.format(json_obj['DriverLogFile'])
    return_str += 'State: {}'.format(json_obj['State'])
    return return_str


def batch_create_parameter_entry(name, kind, direction):
    """

    :param name: str name of the parameter, in the form "<name>[=<default_value>]"
    :param kind: str kind of parameter (Reference|Value)
    :param direction: str direction of parameter (Input|Output)
    :return: dict encoding of the parameter for transmission to SparkBatch
    """
    return_value = {"Id": name,
                    "IsRuntime": True,
                    "IsOptional": False,
                    "Kind": kind,
                    "Direction": direction}
    if '=' in name:
        # need default value
        return_value['Id'] = name.split('=')[0]
        return_value['Value'] = '='.join(name.split('=')[1:])

    return return_value


def batch_create_parameter_list(arg_list):
    """

    :param arg_list: list of tuples of the form [(name, direction, kind)]
            name: str name of the parameter, in the form "<name>[=<default_value>]"
            direction: str direction of the parameter (Input|Output)
            kind: str kind of the parameter (Reference|Value)
    :return: list of dicts encoding the paramaters for transmission to SparkBatch
    """
    return [batch_create_parameter_entry(name, kind, direction)
            for (name, direction, kind) in arg_list]


def batch_app_is_installed():
    """

    :return: int response code, None if connection error
    """
    url = batch_get_url(BATCH_HEALTH_FMT, hdi_domain)
    try:
        resp = requests.get(url, auth=(hdi_user, hdi_pw))
        return resp.status_code
    except requests.exceptions.ConnectionError:
        return None


def batch_get_acceptable_storage():
    """

    :return: list of str - names of acceptable storage returned from the
    """
    url = batch_get_url(BATCH_DEPLOYMENT_INFO_FMT, hdi_domain)
    try:
        success, content = get_success_and_resp_str(
            requests.get(url, auth=(hdi_user, hdi_pw)))
    except requests.ConnectionError:
        raise InvalidStorageException(
            "Error connecting to {}. Please confirm SparkBatch app is healthy.".format(
                url))

    if not success:
        raise InvalidStorageException(content)
    deployment_info = get_json(content)
    if 'Storage' not in deployment_info:
        raise InvalidStorageException('No storage found in deployment info.')

    return [info['Value'].strip() for info in deployment_info['Storage']]


def batch_env_is_valid():
    """

    :return: bool True if all of the following are true:
        1. environment specifies a SparkBatch location
        2. the app at that location is healthy
    """
    hdi_exists = False
    app_present = False
    if not in_local_mode() and (not hdi_domain or not hdi_user or not hdi_pw):
        print("")
        print("Environment is missing the following variables:")
        if not hdi_domain:
            print("  AML_HDI_CLUSTER")
        if not hdi_user:
            print("  AML_HDI_USER")
        if not hdi_pw:
            print("  AML_HDI_PW")
        print("For help setting up environment, run")
        print("  aml env about")
        print("")
    else:
        hdi_exists = True

    # check if the app is installed via health api
    if hdi_exists:
        app_ping_return_code = batch_app_is_installed()
        if app_ping_return_code is None or app_ping_return_code == 404:
            print("AML Batch is not currently installed on {0}. "
                  "Please install the app.".format(batch_get_url(BATCH_URL_BASE_FMT,
                                                                 hdi_domain)))
        elif app_ping_return_code == 200:
            app_present = True
        elif app_ping_return_code == 403:
            print('Authentication failed on {}. Check your AML_HDI_USER and '
                  'AML_HDI_PW environment variables.'.format(
                      batch_get_url(BATCH_URL_BASE_FMT, hdi_domain)))
            print("For help setting up environment, run")
            print("  aml env about")
            print("")
        else:
            print('Unexpected return code {} when querying AzureBatch '
                  'at {}.'.format(app_ping_return_code,
                                  batch_get_url(BATCH_URL_BASE_FMT, hdi_domain)))
            print("If this error persists, contact the SparkBatch team for more "
                  "information.")
    return hdi_exists and app_present


def batch_env_and_storage_are_valid():
    """

    :return: bool True if all of the following are true:
        1. environment specifies a SparkBatch location
        2. the app at that location is healthy
        3. storage is defined in the environment
        4. the storage matches the storage associated with the SparkBatch app (for HDI)
    """
    # Validate that env is set up correctly
    storage_exists = False

    if not batch_env_is_valid():
        return False

    if not in_local_mode() and (not az_account_name or not az_account_key):
        print("")
        print("Environment is missing the following variables:")
        if not az_account_name:
            print("  AML_STORAGE_ACCT_NAME")
        if not az_account_key:
            print("  AML_STORAGE_ACCT_KEY.")
        print("For help setting up environment, run")
        print("  aml env about")
        print("")
    else:
        storage_exists = True

    try:
        acceptable_storage = batch_get_acceptable_storage()
    except InvalidStorageException as exc:
        print("Error retrieving acceptable storage from SparkBatch: {}".format(exc))
        return False

    storage_is_acceptable = in_local_mode() or az_account_name in acceptable_storage
    if not storage_is_acceptable:
        print("Environment storage account {0} not found when querying server "
              "for acceptable storage. Available accounts are: "
              "{1}".format(az_account_name, ', '.join(acceptable_storage)))

    return storage_exists and storage_is_acceptable


def print_batch_publish_usage():
    """
    prints usage statement for batch create
    :return: None
    """
    print("aml service create batch "
          "-n <service name> "
          "-f <webservice file> "
          "[-i <input>[=<default_value>] [-i <input>[=<default_value>]...]] "
          "[-o <output>[=<default_value>] [-o <output>[=<default_value>] ...]] "
          "[-p <parameter>[=<default_value>] [-p <parameter>[=<default_value>]...]] "
          "[-d <dependency> [-d <dependency>...]] "
          "[-v]")


def print_batch_view_usage():
    """
    prints usage statement for batch view service
    :return: None
    """
    print("aml service view batch "
          "-n <service name> ")


def print_batch_score_usage():
    """
    prints usage statement for batch run
    :return: None
    """
    print("aml service run batch "
          "-n <service name> "
          "[-j <job id>] "
          "[-i <input>=<value> [-i <input>=<value>...]] "
          "[-o <output>=<value> [-o <output>=<value> ...]] "
          "[-p <parameter>=<value> [-p <parameter>=<value>...]] "
          "[-w] "
          "[-v]")


def print_batch_viewjob_usage():
    """
    prints usage statement for batch view job
    :return: None
    """
    print('aml service viewjob batch '
          "-n <service name> "
          "-j <job id> "
         )


def print_batch_canceljob_usage():
    """
    prints usage statement for batch cancel job
    :return: None
    """
    print('aml service canceljob batch '
          "-n <service name> "
          "-j <job id> "
         )


def print_batch_list_jobs_usage():
    """
    prints usage statement for batch list jobs
    :return: None
    """
    print('aml service listjobs batch '
          "-n <service name> "
         )


def print_batch_delete_usage():
    """
    prints usage statement for batch delete service
    :return: None
    """
    print('aml service delete batch '
          "-n <service name> "
         )


class BatchEnvironmentFunction(ValueFunction):
    """
    ValueFunction object for use displaying the current environment
    """
    def evaluate(self):
        return BATCH_URL_BASE_FMT.format(hdi_domain)


class ScoringUrlFunction(ValueFunction):
    """
    ValueFunction object for use displaying API endpoint of a service
    """
    def evaluate(self):
        return batch_get_url(BATCH_SINGLE_JOB_FMT, hdi_domain, self.json_obj['Id'],
                             '<job_id>')

batch_create_service_header_to_fn_dict = OrderedDict(
    [('Name', TraversalFunction(('Id',))), ('Environment', BatchEnvironmentFunction())])


batch_list_service_header_to_fn_dict = OrderedDict(
    [('Name', TraversalFunction(('Name',))),
     ('Last_Modified_at', TraversalFunction(('ModificationTimeUtc',))),
     ('Environment', BatchEnvironmentFunction())
    ])

batch_list_jobs_header_to_fn_dict = OrderedDict(
    [('Name', TraversalFunction(('Name',))),
     ('Last_Modified_at', TraversalFunction(('ModificationTimeUtc',))),
     ('Environment', BatchEnvironmentFunction())])

batch_view_service_header_to_fn_dict = OrderedDict(
    [('Name', TraversalFunction(('Id',))),
     ('Environment', BatchEnvironmentFunction())])

batch_view_service_usage_header_to_fn_dict = OrderedDict(
    [('Scoring_url', ScoringUrlFunction()),
     ('Inputs',
      ConditionalListTraversalFunction(
          ('Parameters',),
          condition=lambda param: (param['Kind'] == 'Reference' and
                                   param['Direction'] == 'Input'),
          action=lambda param: param['Id'])),
     ('Outputs', ConditionalListTraversalFunction(
         ('Parameters',),
         condition=lambda param: (param['Kind'] == 'Reference' and
                                  param['Direction'] == 'Output'),
         action=lambda param: param['Id'])),
     ('Parameters', ConditionalListTraversalFunction(
         ('Parameters',),
         condition=lambda param: (param['Kind'] == 'Value' and
                                  param['Direction'] == 'Input'),
         action=lambda param: param['Id']))
    ])
