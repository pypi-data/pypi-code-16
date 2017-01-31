# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Utility functions for AML CLI
"""

from __future__ import print_function
import os
import json
import uuid
import re
from builtins import input
from datetime import datetime, timedelta

try:
    # python 3
    from urllib.request import pathname2url
    from urllib.parse import urljoin, urlparse  # pylint: disable=unused-import
except ImportError:
    # python 2
    from urllib import pathname2url
    from urlparse import urljoin, urlparse

from tabulate import tabulate
import requests
from azure.storage.blob import BlockBlobService
from azuremlcli import __version__
import subprocess
import re

# CONSTANTS
hdi_home_regex = r'(.*:\/\/)?(?P<cluster_name>[^\s]*)'
aml_env_default_location = 'east us'
az_account_name = os.environ.get('AML_STORAGE_ACCT_NAME')
az_account_key = os.environ.get('AML_STORAGE_ACCT_KEY')
acs_master_url = os.environ.get('AML_ACS_MASTER')
acs_agent_url = os.environ.get('AML_ACS_AGENT')
acr_home = os.environ.get('AML_ACR_HOME')
acr_user = os.environ.get('AML_ACR_USER')
acr_pw = os.environ.get('AML_ACR_PW')
hdi_home = os.environ.get('AML_HDI_CLUSTER')
if hdi_home:
    match_obj = re.match(hdi_home_regex, hdi_home)
    if match_obj:
        hdi_home = match_obj.group('cluster_name')

hdi_user = os.environ.get('AML_HDI_USER', '')
hdi_pw = os.environ.get('AML_HDI_PW', '')
hdi_domain = hdi_home.split('.')[0] if hdi_home else None

ice_base_url = 'https://amlacsagent.azureml-int.net'
acs_connection_timeout = 5
ice_connection_timeout = 5


# EXCEPTIONS
class InvalidConfError(Exception):
    """Exception raised when config read from file is not valid json."""
    pass


# UTILITY FUNCTIONS
def get_json(payload):
    """
    Handles decoding JSON to python objects in py2, py3
    :param payload: str/bytes json to decode
    :return: dict/list/str that represents json
    """
    if isinstance(payload, bytes):
        payload = payload.decode('utf-8')
    return json.loads(payload) if payload else {}


def get_home_dir():
    """
    Function to find home directory on windows or linux environment
    :return: str - path to home directory
    """
    return os.path.expanduser('~')


def read_config():
    """

    Tries to read in ~/.amlconf as a dictionary.
    :return: dict - if successful, the config dictionary from ~/.amlconf, None otherwise
    :raises: InvalidConfError if the configuration read is not valid json, or is not a dictionary
    """
    home_dir = get_home_dir()
    try:
        with open(home_dir + '/.amlconf', 'r') as conf_file:
            conf = conf_file.read()
    except IOError:
        return None
    try:
        conf = json.loads(conf)
    except ValueError:
        raise InvalidConfError

    if not isinstance(conf, dict):
        raise InvalidConfError

    return conf


def write_config(conf):
    """

    Writes out the given configuration dictionary to ~/.amlconf.
    :param conf: Configuration dictionary.
    :return: 0 if success, -1 otherwise
    """
    conf = json.dumps(conf)
    home_dir = get_home_dir()
    try:
        with open(home_dir + '/.amlconf', 'w') as conf_file:
            conf_file.write(conf)
    except IOError:
        return -1

    return 0


def in_local_mode():
    """
    Determines if AML CLI is running in local mode
    :return: bool - True if in local mode, false otherwise
    """

    try:
        conf = read_config()
        if conf and 'mode' in conf:
            if conf['mode'] == 'local':
                return True
    except InvalidConfError:
        print('Warning: Azure ML configuration file is corrupt.')
        print('Resetting to local mode.')
        conf = {'mode': 'local'}
        write_config(conf)
        return True

    return False


def check_version(conf):
    """

    :param conf: dict configuration dictionary
    :return: None
    """
    try:
        p = subprocess.Popen('pip list -o --pre', shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        output, err = p.communicate()
        if isinstance(output, bytes):
            output = output.decode('utf-8')

        version_regex = r'azuremlcli \((?P<current>[^\)]+)\) - Latest: (?P<latest>[^ ]+)'
        search_obj = re.search(version_regex, output)
        if search_obj:
            print('\033[93mYou are using AzureML CLI version {}, '
                  'but version {} is available.'.format(
                      search_obj.group('current'), search_obj.group('latest')))
            print("You should consider upgrading via the 'pip install --upgrade "
                  "azuremlcli' command.\033[0m")
            print()
        conf['next_version_check'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        write_config(conf)
    except Exception as exc:
        print('Warning: Error determining if there is a newer version of AzureML CLI available: {}'.format(
            exc))


def first_run():
    """
    Determines if this is the first run (either no config file,
    or config file missing api key). In either case, it prompts
    the user to enter an api key, and validates it. If invalid,
    asks user if they want to continue and add a key at a later
    time. Also sets mode to local if this is the first run.
    Verifies version of CLI as well.
    """

    is_first_run = False
    is_config_corrupt = False
    conf = {}

    try:
        conf = read_config()
        if conf:
            try:
                need_version_check = 'next_version_check' not in conf or datetime.now() > datetime.strptime(
                    conf['next_version_check'], '%Y-%m-%d')
            except ValueError:
                need_version_check = True

            if need_version_check:
                check_version(conf)
        else:
            is_first_run = True
            conf = {}
    except InvalidConfError:
        print('Warning: Azure ML configuration file is corrupt.')
        is_config_corrupt = True

    if is_first_run or is_config_corrupt:
        conf['mode'] = 'local'
        check_version(conf)
        write_config(conf)


def get_success_and_resp_str(http_response, response_obj=None, verbose=False):
    """

    :param http_response: requests.response object
    :param response_obj: Response object to format a successful response
    :return: (bool, str) - (result, result_str)
    """
    if http_response is None:
        return False, "Response was None."
    if verbose:
        print(http_response.content)
    if http_response.status_code == 200:
        json_obj = get_json(http_response.content)
        if response_obj is not None:
            return True, response_obj.format_successful_response(json_obj)
        return True, json.dumps(json_obj, indent=4, sort_keys=True)
    else:
        return False, process_errors(http_response)


def process_errors(http_response):
    """

    :param http_response:
    :return: str message for parsed error
    """
    try:
        json_obj = get_json(http_response.content)
        to_print = '\n'.join([detail['message'] for detail in json_obj['error']['details']])
    except KeyError:
        to_print = http_response.content

    return 'Failed.\nResponse code: {}\n{}'.format(http_response.status_code, to_print)


def validate_remote_filepath(filepath):
    """
    Throws exception if remote filepath is invalid.

    :param filepath: str path to asset file. Should be http or wasb.
    :return: None
    """
    if in_local_mode():
        raise ValueError('Remote paths ({}) are not supported in local mode. '
                         'Please specify a local path.'.format(filepath))
    if not filepath.startswith('wasb:///') and not filepath.startswith('wasbs:///') \
            and az_account_name not in filepath:
        # note - wasb[s]:/// indicates to HDI cluster to use default storage backing
        raise ValueError('Remote paths ({}) must be on the backing '
                         'storage ({})'.format(filepath, az_account_name))


def update_asset_path(verbose, filepath, container, is_input=True):
    """

    :param verbose: bool True => Debug messages
    :param filepath: str path to asset file. Can be http, wasb, or local file
    :param container: str name of the container to upload to (azureml/$(container)/assetID)
    :param is_input: bool True if asset will be used as an input
    :return: (str, str) (asset_id, location)
    """

    asset_id = os.path.split(filepath)[1]

    if filepath.startswith('http') or filepath.startswith('wasb'):
        validate_remote_filepath(filepath)

        # return remote resources as is
        return asset_id, filepath

    # convert relative paths
    filepath = os.path.abspath(os.path.expanduser(filepath))

    # verify that file exists
    if is_input and not os.path.exists(filepath):
        raise ValueError('{} does not exist or is not accessible'.format(filepath))

    if in_local_mode():
        return asset_id, urljoin('file:', pathname2url(filepath))

    if not is_input:
        raise ValueError('Local output paths ({}) are not supported in remote mode. '
                         'Please use a https or wasbs path on the backing '
                         'storage ({})'.format(filepath, az_account_name))

    if verbose:
        print('filepath: {}'.format(filepath))
        print('container: {}'.format(container))

    if os.path.isfile(filepath):
        return upload_resource(filepath, container, asset_id, verbose)
    elif os.path.isdir(filepath):
        wasb_path = None
        to_strip = os.path.split(filepath)[0]
        # directory
        for dirpath, _, files in os.walk(filepath):
            for walk_fp in files:
                to_upload = os.path.join(dirpath, walk_fp)
                container_for_upload = '{}/{}'.format(container, to_upload[len(to_strip) + 1:-(len(walk_fp) + 1)])
                _, wasb_path = upload_resource(to_upload, container_for_upload, walk_fp,
                                               verbose)

        if wasb_path is None:
            raise ValueError('Directory {} was empty.'.format(filepath))

        asset_id = os.path.basename(filepath)
        match_obj = re.match(r'(?P<wasb_path>.*{})'.format(os.path.basename(filepath)),
                             wasb_path)
        if match_obj:
            return asset_id, match_obj.group('wasb_path')
        raise ValueError('Unable to parse upload location.')
    else:
        raise ValueError('Resource uploads are only supported for files and directories.')


def upload_resource(filepath, container, asset_id, verbose):
    """
    Function to upload local resource to blob storage
    :param filepath: str path of file to upload
    :param container: str name of subcontainer inside azureml container
    :param asset_id: str name of asset inside subcontainer
    :param verbose: bool verbosity flag
    :return: str, str : uploaded asset id, blob location
    """
    az_container_name = 'azureml'
    # with open(filepath) as asset_file:
    #     code = asset_file.read()
    az_blob_name = '{}/{}'.format(container, asset_id)
    bbs = BlockBlobService(account_name=az_account_name,
                           account_key=az_account_key)
    bbs.create_container(az_container_name)
    bbs.create_blob_from_path(az_container_name, az_blob_name, filepath)
    wasb_package_location = 'wasbs://{}@{}.blob.core.windows.net/' \
                            '{}'.format(az_container_name, az_account_name, az_blob_name)
    if verbose:
        print("Asset {} uploaded to {}".format(filepath, wasb_package_location))
    return asset_id, wasb_package_location


def traverse_json(json_obj, traversal_tuple):
    """
        Example:
            {
                "ID": "12345",
                "Properties" {
                    "Name": "a_service"
                }
            }

            If we wanted the "Name" property of the above json to be displayed, we would use the traversal_tuple
                ("Properties", "Name")

        NOTE that list traversal is not supported here.

    :param json_obj: json_obj to traverse. nested dictionaries--lists not supported
    :param traversal_tuple: tuple of keys to traverse the json dict
    :return: string value to display
    """
    trav = json_obj
    for key in traversal_tuple:
        trav = trav[key]
    return trav


class Response(object):  # pylint: disable=too-few-public-methods
    """
    Interface for use constructing response strings from json object for successful requests
    """
    def format_successful_response(self, json_obj):
        """

        :param json_obj: json object from successful response
        :return: str response to print to user
        """
        raise NotImplementedError('Class does not implement format_successful_response')


class StaticStringResponse(Response):  # pylint: disable=too-few-public-methods
    """
    Class for use constructing responses that are a static string for successful requests.
    """
    def __init__(self, static_string):
        self.static_string = static_string

    def format_successful_response(self, json_obj):
        """

        :param json_obj: json object from successful response
        :return: str response to print to user
        """
        return self.static_string


class TableResponse(Response):
    """
    Class for use constructing response tables from json object for successful requests
    """
    def __init__(self, header_to_value_fn_dict):
        """

        :param header_to_value_fn_dict: dictionary that maps header (str) to a tuple that defines how to
        traverse the json object returned from the service
        """
        self.header_to_value_fn_dict = header_to_value_fn_dict

    def create_row(self, json_obj, headers):
        """

        :param json_obj: list or dict to present as table
        :param headers: list of str: headers of table
        :return:
        """
        return [self.header_to_value_fn_dict[header].set_json(json_obj).evaluate()
                for header in headers]

    def format_successful_response(self, json_obj):
        """

        :param json_obj: list or dict to present as table
        :return: str response to print to user
        """
        rows = []
        headers = self.header_to_value_fn_dict.keys()
        if isinstance(json_obj, list):
            for inner_obj in json_obj:
                rows.append(self.create_row(inner_obj, headers))
        else:
            rows.append(self.create_row(json_obj, headers))
        return tabulate(rows, headers=[header.upper() for header in headers], tablefmt='psql')


class MultiTableResponse(TableResponse):
    """
    Class for use building responses with multiple tables
    """
    def __init__(self, header_to_value_fn_dicts):  # pylint: disable=super-init-not-called
        """

        :param header_to_value_fn_dicts:
        """

        self.header_to_value_fn_dicts = header_to_value_fn_dicts

    def format_successful_response(self, json_obj):
        result = ''
        for header_to_value_fn_dict in self.header_to_value_fn_dicts:
            self.header_to_value_fn_dict = header_to_value_fn_dict
            result += super(MultiTableResponse, self).format_successful_response(json_obj)
            result += '\n'
        return result


class StaticStringWithTableReponse(TableResponse):
    """
    Class for use constructing response that is a static string and tables from json object for successful requests
    """
    def __init__(self, static_string, header_to_value_fn_dict):
        """
        :param static_string: str that will be printed after table
        :param header_to_value_fn_dict: dictionary that maps header (str) to a tuple that defines how to
        traverse the json object returned from the service
        """
        super(StaticStringWithTableReponse, self).__init__(header_to_value_fn_dict)
        self.static_string = static_string

    def format_successful_response(self, json_obj):
        return '\n\n'.join([super(StaticStringWithTableReponse, self).format_successful_response(json_obj),
                            self.static_string])


class ValueFunction(object):
    """
    Abstract class for use finding the appropriate value for a given property in a json response.
         defines set_json, a function for storing the json response we will format
         declares evaluate, a function for retrieving the formatted string
    """
    def __init__(self):
        self.json_obj = None

    def set_json(self, json_obj):
        """

        :param json_obj: list or dict to store for processing
        :return: ValueFunction the "self" object with newly updated json_obj member
        """
        self.json_obj = json_obj
        return self

    def evaluate(self):
        """

        :return: str value to display
        """
        raise NotImplementedError("Class does not implement evaluate method.")


class TraversalFunction(ValueFunction):
    """
    ValueFunction that consumes a traversal tuple to locate the appropriate string for display
        Example:
            {
                "ID": "12345",
                "Properties" {
                    "Name": "a_service"
                }
            }

            If we wanted the "Name" property of the above json to be displayed, we would use the traversal_tuple
                ("Properties", "Name")

        NOTE that list traversal is not supported here.
    """
    def __init__(self, tup):
        super(TraversalFunction, self).__init__()
        self.traversal_tup = tup

    def evaluate(self):
        return traverse_json(self.json_obj, self.traversal_tup)


class ConditionalListTraversalFunction(TraversalFunction):
    """
    Class for use executing actions on members of a list that meet certain criteria
    """
    def __init__(self, tup, condition, action):
        super(ConditionalListTraversalFunction, self).__init__(tup)
        self.condition = condition
        self.action = action

    def evaluate(self):
        json_list = super(ConditionalListTraversalFunction, self).evaluate()
        return ', '.join([self.action(item) for item in json_list if self.condition(item)])


def version():
    """

    Prints the version of the package as defined in __init__.py
    :return:
    """
    print('Azure Machine Learning Command Line Tools {}'.format(__version__))


def is_int(int_str):
    """

    Check whether the given variable can be cast to int
    :param int_str: the variable to check
    :return: bool
    """
    try:
        int(int_str)
        return True
    except ValueError:
        return False
