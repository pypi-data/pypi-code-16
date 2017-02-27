"""
Contains batch workflows for AzureML cli
"""

import time
import getopt
import uuid
import json
import requests
from pkg_resources import resource_string

from azuremlcli.cli_util import get_json
from azuremlcli.cli_util import get_success_and_resp_str
from azuremlcli.cli_util import update_asset_path
from azuremlcli.cli_util import StaticStringResponse
from azuremlcli.cli_util import TableResponse
from azuremlcli.cli_util import MultiTableResponse
from azuremlcli.cli_util import StaticStringWithTableReponse

from azuremlcli.batchutilities import BATCH_ALL_WS_FMT
from azuremlcli.batchutilities import BATCH_SINGLE_WS_FMT
from azuremlcli.batchutilities import BATCH_ALL_JOBS_FMT
from azuremlcli.batchutilities import BATCH_SINGLE_JOB_FMT
from azuremlcli.batchutilities import BATCH_CANCEL_JOB_FMT
from azuremlcli.batchutilities import batch_get_asset_type
from azuremlcli.batchutilities import batch_get_parameter_str
from azuremlcli.batchutilities import batch_create_parameter_list
from azuremlcli.batchutilities import batch_get_job_description
from azuremlcli.batchutilities import batch_env_and_storage_are_valid
from azuremlcli.batchutilities import batch_env_is_valid
from azuremlcli.batchutilities import batch_get_url
from azuremlcli.batchutilities import print_batch_canceljob_usage
from azuremlcli.batchutilities import print_batch_delete_usage
from azuremlcli.batchutilities import print_batch_list_jobs_usage
from azuremlcli.batchutilities import print_batch_publish_usage
from azuremlcli.batchutilities import print_batch_score_usage
from azuremlcli.batchutilities import print_batch_view_usage
from azuremlcli.batchutilities import print_batch_viewjob_usage
from azuremlcli.batchutilities import batch_list_service_header_to_fn_dict
from azuremlcli.batchutilities import batch_view_service_header_to_fn_dict
from azuremlcli.batchutilities import batch_view_service_usage_header_to_fn_dict
from azuremlcli.batchutilities import batch_create_service_header_to_fn_dict
from azuremlcli.batchutilities import batch_list_jobs_header_to_fn_dict
from azuremlcli.batchutilities import batch_get_job

def batch_service_run(context, args):
    """
    Processing for starting a job on an existing batch service
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    :return: None
    """
    service_name = ''
    job_name = time.strftime('%Y-%m-%d_%H%M%S')
    verbose = False
    valid_parameters = True
    parameters = {}
    wait_for_completion = False
    try:
        opts, args = getopt.getopt(args, "n:i:o:p:j:vw")
    except getopt.GetoptError as exc:
        print(exc)
        print_batch_score_usage()
        return

    parameters_container = 'parameters{}'.format(uuid.uuid4())
    for opt, arg in opts:
        if opt == '-n':
            service_name = arg
        elif opt == '-j':
            job_name = arg
        elif opt == '-w':
            wait_for_completion = True
        elif opt == '-v':
            verbose = True
        elif opt == '-i' or opt == '-o' or opt == '-p':
            if '=' not in arg:
                valid_parameters = False
                print("Must provide value for parameter {0}".format(arg))
            else:
                parameters[arg.split('=')[0]] = ("=".join(arg.split('=')[1:]), opt)

    if not service_name or not valid_parameters:
        print_batch_score_usage()
        return

    # validate environment
    if not batch_env_and_storage_are_valid(context):
        return

    # upload any local parameters if needed
    try:
        parameters = {param_name: update_asset_path(context, verbose,
                                                    parameters[param_name][0],
                                                    parameters_container,
                                                    is_input=parameters[param_name][1] == '-i')[1]
                      for param_name in parameters}
    except ValueError as exc:
        print('Unable to process parameters: {}'.format(exc))
        return

    if verbose:
        print('parameters: {0}'.format(parameters))

    arg_payload = {'Parameters': parameters}

    url = batch_get_url(context, BATCH_SINGLE_JOB_FMT, service_name, job_name)
    if verbose:
        print('scoring at {}'.format(url))
    headers = {'Content-Type': 'application/json'}
    try:
        resp = context.http_call('put', url,
                                 headers=headers,
                                 data=json.dumps(arg_payload),
                                 auth=(context.hdi_user, context.hdi_pw))
    except requests.ConnectionError:
        print("Error connecting to {}. Please confirm SparkBatch app is healthy.".format(url))
        return

    succeeded, to_print = get_success_and_resp_str(context, resp, response_obj=StaticStringResponse(
        'Job {0} submitted on service {1}.'.format(job_name, service_name)), verbose=verbose)
    print(to_print)
    if not succeeded:
        return

    if wait_for_completion:
        while True:
            succeeded, to_print = get_success_and_resp_str(context,
                                                           batch_get_job(context, job_name, service_name, verbose),
                                                           verbose=verbose)
            if not succeeded:
                print(to_print)
                return
            resp_obj = get_json(to_print)
            job_state = resp_obj['State']
            if 'YarnAppId' in resp_obj:
                print('{}: {}'.format(resp_obj['YarnAppId'], job_state))
            else:
                print(job_state)
            if job_state == 'NotStarted' or job_state == 'InProgress':
                time.sleep(5)
            else:
                print(batch_get_job_description(context, to_print))
                break
    else:
        print('To check job status, run: aml service viewjob batch -n {} -j {}'.format(service_name, job_name))


def batch_view_job(context, args):
    """
    Processing for viewing a job on an existing batch service
    :param context: CommandLineInterfaceContext object
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    :return: None
    """
    service_name = ''
    job_name = ''
    verbose = False
    try:
        opts, args = getopt.getopt(args, "n:j:v")
    except getopt.GetoptError as exc:
        print(exc)
        print_batch_viewjob_usage()
        return

    for opt, arg in opts:
        if opt == '-j':
            job_name = arg
        elif opt == '-n':
            service_name = arg
        elif opt == '-v':
            verbose = True

    if not job_name or not service_name:
        print_batch_viewjob_usage()
        return

    if not batch_env_is_valid(context):
        return

    success, content = get_success_and_resp_str(context, batch_get_job(context, job_name, service_name, verbose),
                                                verbose=verbose)
    if success:
        print(batch_get_job_description(context, content))
    else:
        print(content)


def batch_service_view(context, args):
    """
    Processing for viewing an existing batch service
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    :return: None
    """
    if not batch_env_is_valid(context):
        return
    service_name = ''
    verbose = False

    try:
        opts, args = getopt.getopt(args, "n:v")
    except getopt.GetoptError as exc:
        print(exc)
        print_batch_view_usage()
        return
    for opt, arg in opts:
        if opt == '-n':
            service_name = arg
        if opt == '-v':
            verbose = True

    if not service_name:
        print_batch_view_usage()
        return

    url = batch_get_url(context, BATCH_SINGLE_WS_FMT, service_name)
    try:
        resp = context.http_call('get', url, auth=(context.hdi_user, context.hdi_pw))

        success, response = get_success_and_resp_str(context, resp, response_obj=MultiTableResponse(
            [batch_view_service_header_to_fn_dict, batch_view_service_usage_header_to_fn_dict]), verbose=verbose)
        print(response)
        if success:
            param_str = ' '.join([batch_get_parameter_str(p) for
                                  p in sorted(resp.json()['Parameters'],
                                              key=lambda x: '_' if 'Value' in x
                                              else x['Direction'])])
            usage = 'Usage: aml service run batch -n {} {} [-w] [-j <job_id>] [-v]'.format(service_name,
                                                                                           param_str)
            print(usage)

    except requests.ConnectionError:
        print("Error connecting to {}. Please confirm SparkBatch app is healthy.".format(url))
        return


def batch_service_list(context):
    """
    Processing for listing existing batch services
    :param context: CommandLineInterfaceContext object
    :return: None
    """
    if not batch_env_is_valid(context):
        return
    url = batch_get_url(context, BATCH_ALL_WS_FMT)
    try:
        resp = context.http_call('get', url, auth=(context.hdi_user, context.hdi_pw))
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(
            batch_list_service_header_to_fn_dict))[1])
    except requests.ConnectionError:
        print("Error connecting to {}. Please confirm SparkBatch app is healthy.".format(url))
        return


def batch_list_jobs(context, args):
    """
    Processing for listing all jobs of an existing batch service
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    :return: None
    """
    if not batch_env_is_valid(context):
        return
    service_name = ''

    try:
        opts, args = getopt.getopt(args, "n:")
    except getopt.GetoptError as exc:
        print(exc)
        print_batch_view_usage()
        return
    for opt, arg in opts:
        if opt == '-n':
            service_name = arg

    if not service_name:
        print_batch_list_jobs_usage()
        return

    url = batch_get_url(context, BATCH_ALL_JOBS_FMT, service_name)
    try:
        resp = context.http_call('get', url, auth=(context.hdi_user, context.hdi_pw))
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(batch_list_jobs_header_to_fn_dict))[1])
    except requests.ConnectionError:
        print("Error connecting to {}. Please confirm SparkBatch app is healthy.".format(url))
        return


def batch_cancel_job(context, args):
    """
    Processing for canceling a job on an existing batch service
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    :return: None
    """
    if not batch_env_is_valid(context):
        return
    service_name = ''
    job_name = ''
    verbose = False
    try:
        opts, args = getopt.getopt(args, "n:j:v")
    except getopt.GetoptError as exc:
        print(exc)
        print_batch_canceljob_usage()
        return

    for opt, arg in opts:
        if opt == '-j':
            job_name = arg
        elif opt == '-n':
            service_name = arg
        elif opt == '-v':
            verbose = True

    if not job_name or not service_name:
        print_batch_canceljob_usage()
        return

    url = batch_get_url(context, BATCH_CANCEL_JOB_FMT, service_name, job_name)
    if verbose:
        print("Canceling job by posting to {}".format(url))
    try:
        resp = context.http_call('post', url, auth=(context.hdi_user, context.hdi_pw))
        print(get_success_and_resp_str(context, resp, response_obj=StaticStringResponse(
            'Job {0} of service {1} canceled.'.format(job_name, service_name)), verbose=verbose)[1])
    except requests.ConnectionError:
        print("Error connecting to {}. Please confirm SparkBatch app is healthy.".format(url))
        return


def batch_service_delete(context, args):
    """
    Processing for deleting a job on an existing batch service
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    :return: None
    """
    service_name = ''
    verbose = False
    try:
        opts, args = getopt.getopt(args, "n:v")
    except getopt.GetoptError as exc:
        print(exc)
        print_batch_delete_usage()
        return
    for opt, arg in opts:
        if opt == '-n':
            service_name = arg
        elif opt == '-v':
            verbose = True

    if not service_name:
        print_batch_delete_usage()
        return

    if not batch_env_and_storage_are_valid(context):
        return

    url = batch_get_url(context, BATCH_SINGLE_WS_FMT, service_name)

    try:
        resp = context.http_call('get', url, auth=(context.hdi_user, context.hdi_pw))
    except requests.ConnectionError:
        print("Error connecting to {}. Please confirm SparkBatch app is healthy.".format(url))
        return

    exists, err_msg = get_success_and_resp_str(context, resp, verbose=verbose)
    if not exists:
        print(err_msg)
        return

    if verbose:
        print('Deleting resource at {}'.format(url))
    try:
        resp = context.http_call('delete', url, auth=(context.hdi_user, context.hdi_pw))
    except requests.ConnectionError:
        print("Error connecting to {}. Please confirm SparkBatch app is healthy.".format(url))
        return
    print(get_success_and_resp_str(context, resp, response_obj=StaticStringResponse(
        'Service {} deleted.'.format(service_name)), verbose=verbose)[1])


def batch_service_create(context, args):
    """
    Processing for creating a new batch service
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    :return: None
    """
    driver_file = ''
    service_name = ''
    title = ''
    verbose = False
    inputs = []
    outputs = []
    parameters = []
    dependencies = []
    try:
        opts, args = getopt.getopt(args, "f:n:i:o:p:d:t:v")
    except getopt.GetoptError as exc:
        print(exc)
        print_batch_publish_usage()
        return

    for opt, arg in opts:
        if opt == '-f':
            driver_file = arg
        elif opt == '-n':
            service_name = arg
        elif opt == '-v':
            verbose = True
        elif opt == '-i':
            inputs.append((arg, 'Input', 'Reference'))
        elif opt == '-o':
            outputs.append((arg, 'Output', 'Reference'))
        elif opt == '-p':
            parameters.append((arg, 'Input', 'Value'))
        elif opt == '-d':
            dependencies.append(arg)
        elif opt == '-t':
            title = arg

    if not driver_file or not service_name:
        print_batch_publish_usage()
        return

    if verbose:
        print('outputs: {0}'.format(outputs))
        print('inputs: {0}'.format(inputs))
        print('parameters: {0}'.format(parameters))

    if not batch_env_and_storage_are_valid(context):
        return

    if not title:
        title = service_name

    # DEPENDENCIES
    dependency_container = 'dependencies/{}'.format(uuid.uuid4())
    try:
        dependencies = [update_asset_path(context, verbose, dependency, dependency_container) for dependency in dependencies]
    except ValueError as exc:
        print('Error uploading dependencies: {}'.format(exc))
        return

    # DRIVER
    try:
        driver_id, driver_uri = update_asset_path(context, verbose, driver_file, dependency_container)
    except ValueError as exc:
        print('Error uploading driver: {}'.format(exc))
        return

    # modify json payload to update driver package location
    payload = resource_string(__name__, 'data/batch_create_payload.json')
    json_payload = get_json(payload)

    json_payload['Assets'] = [{'Id': driver_id, 'Uri': driver_uri}]
    json_payload['Package']['DriverProgramAsset'] = driver_id

    # OTHER DEPENDENCIES
    for dependency in dependencies:
        json_payload['Assets'].append({'Id': dependency[0], 'Uri': dependency[1]})
        json_payload['Package'][batch_get_asset_type(dependency[0])].append(
            dependency[0])

    # replace inputs from template
    json_payload['Parameters'] = batch_create_parameter_list(inputs + outputs + parameters)

    # update assets payload for default inputs
    for parameter in json_payload['Parameters']:
        if 'Value' in parameter:
            if parameter['Kind'] == 'Reference':
                try:
                    asset_id, location = update_asset_path(context, verbose, parameter['Value'],
                                                           dependency_container,
                                                           parameter['Direction'] ==
                                                           'Input')
                    json_payload['Assets'].append({'Id': asset_id, 'Uri': location})
                    parameter['Value'] = asset_id
                except ValueError as exc:
                    print('Error creating parameter list: {}'.format(exc))
                    return

    # update title
    json_payload['Title'] = title

    if verbose:
        print('json_payload: {}'.format(json_payload))

    # call SparkBatch with payload to create web service
    url = batch_get_url(context, BATCH_SINGLE_WS_FMT, service_name)

    if verbose:
        print("Creating web service at " + url)

    headers = {'Content-Type': 'application/json'}

    try:
        resp = context.http_call('put', url, headers=headers,
                            data=json.dumps(json_payload),
                            auth=(context.hdi_user, context.hdi_pw))
    except requests.ConnectionError:
        print("Error connecting to {}. Please confirm SparkBatch app is healthy.".format(url))
        return

    # Create usage str: inputs/parameters before ouputs, optional after all
    param_str = ' '.join([batch_get_parameter_str(p) for
                          p in sorted(json_payload['Parameters'],
                                      key=lambda x: '_' if 'Value' in x
                                      else x['Direction'])])

    usage = 'Usage: aml service run batch -n {} {} [-w] [-j <job_id>] [-v]'.format(service_name,
                                                                                   param_str)

    success, response = get_success_and_resp_str(context, resp, response_obj=StaticStringWithTableReponse(
        usage, batch_create_service_header_to_fn_dict), verbose=verbose)
    if success:
        print('Success.')

    print(response)