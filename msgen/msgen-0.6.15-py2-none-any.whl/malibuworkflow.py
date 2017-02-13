# ----------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved. 
#  Licensed under the MIT License. See License.txt in the 
#  project root for license information.  If License.txt is 
#  missing, see https://opensource.org/licenses/MIT
# ----------------------------------------------------------

""" File for all workflow related functionality """
import sys
import time
from time import sleep
from datetime import datetime
try:
    import requests
except ImportError:
    print "You need to install the 'requests' library. Try: pip install requests"
    sys.exit(code=1)

import msgen_cli.malibucommon as malibucommon
import msgen_cli.malibuservice as malibuservice
import msgen_cli.datatransfer as datatransfer

class WorkflowExecutor(object):
    """ Main class for working with workflows """
    def __init__(self, args_output):

        """ Constructor """
        self.args_output = args_output
        malibu_url = malibucommon.get_api_url_from_base(
            self.args_output.api_url_base)

        self.service = malibuservice.MalibuService(
            malibu_url,
            self.args_output.subscription_key)

        storage_info = args_output.get_storage_accounts_info()

        self.datatransfer = datatransfer.AzureDataTransfer(
            args_output.blobxfer_path,
            storage_info,
            self.args_output.azure_as_cache_mode)

        #set exit status code
        self.current_exit_status = None
        self.exit_status_by_result = {
            0:("Success", 0),
            1:("Failure", 1),
            2:("Temporary failure", 100)}

        self.exit_status_by_response = {
            200:("Success", 0),
            400:("Temporary failure", 100),
            401:("Unauthorized", 1000),
            405:("Not allowed", 1000)}

        #workflow status code:{name,sys_exit_code}
        self.exit_status_by_workflow_status = {
            1000:("Queued", 10),
            10000:("In progress", 20),
            20000:("Completed successfully", 0),
            50000:("Failed", 1000),
            58000:("Cancellation requested", 1000),
            60000:("Cancelled", 1000)}

    @property
    def download_output(self):
        """
        Indicates if the outputs will be downloaded
        """
        download = (
            self.args_output.local_output_path != "" and
            self.args_output.local_output_path is not None)

        return download

    @property
    def upload_local_inputs(self):
        """
        Indicates if local inputs will be uploaded
        """
        upload = (
            self.args_output.local_input_1 != "" and
            self.args_output.local_input_1 is not None)

        return upload

    def display_status(self, workflow, response_code=None, short=True):
        """ Displays status of workflow """
        display_message = "NA"
        if workflow.get("Message"):
            display_message = workflow["Message"]
        elif workflow.get("Status") in self.exit_status_by_workflow_status:
            display_message = self.exit_status_by_workflow_status[workflow["Status"]][0]

        print_template = "[{0}] - Message: {1}  Status Code: {2}"
        msg = print_template.format(
            time.strftime("%m/%d/%Y %H:%M:%S"),
            display_message,
            workflow.get("Status"))

        if response_code:
            msg += "  Response Code: {0}".format(response_code)

        if workflow.get("Id") > 0:
            print_template = "[{0} - Workflow ID: {1}]: Message: {2}"
            msg = print_template.format(
                time.strftime("%m/%d/%Y %H:%M:%S"),
                str(workflow["Id"]),
                display_message)
            if not short:
                msg += "\n\tProcess: {0}\n\tDescription: {1}".format(workflow.get("Process"), workflow.get("Description"))

        print msg
        sys.stdout.flush()

    def display_error(self, exception, response_code, status_code):
        """ Display errors  """
        workflow_status = "NA"
        if status_code in self.exit_status_by_workflow_status:
            workflow_status = self.exit_status_by_workflow_status[status_code][0]

        message = "Exception: {0}, Response Code {1}, Status {2} "
        print message.format(str(exception),
                             str(response_code),
                             workflow_status)
    @classmethod
    def workflow_wall_clock_endtime(cls, end_date, created_date_object):
        """ Calculates the end time of a workflow item """
        utc_now = datetime.utcnow()
        time_delta = utc_now - created_date_object
        return_end_date = ""

        if end_date is not None and end_date != "" :
            end_date_parts = str(end_date).split(".")
            end_date_object = datetime.strptime(end_date_parts[0], '%Y-%m-%dT%H:%M:%S')
            time_delta = end_date_object-created_date_object
            return_end_date = str(end_date)

        base_seconds = int(time_delta.total_seconds())
        hours, remainder = divmod(base_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return return_end_date, hours, minutes, seconds

    def post_workflow(self):

        workflow_id = self.post_workflow_blocking()
        if self.args_output.no_poll or workflow_id <= 0:
            return

        self.poll_workflow_status_blocking(workflow_id)

    def post_workflow_blocking(self):
        """ Posts a new workflow to the service """

        if self.upload_local_inputs:
            self.datatransfer.upload_inputs(
                self.args_output.local_input_1,
                self.args_output.local_input_2)

        input_dic, output_dic = self.get_input_and_output_dict()

        try:
            response_code, workflow = self.service.create_workflow_item(
                self.args_output.process_name,
                self.args_output.process_args,
                self.args_output.input_storage_account_type,
                self.args_output.output_storage_account_type,
                input_dic,
                output_dic,
                self.args_output.description,
                self.args_output.workflow_class)

            self.set_exit_code(None, response_code)
            if not workflow.get("Message"):
                workflow["Message"] = "Successfully submitted"

            self.display_status(workflow, response_code, short=False)
            self.args_output.workflow_id = workflow.get("Id", 0)
            return self.args_output.workflow_id

        except requests.exceptions.ConnectionError as exc:
            print ("Could not connect to Malibu REST API."
                   "  Please review the api_url_base setting in config.txt,"
                   " and check your network settings.")
            print "Exception: {0}".format(str(exc))
            self.set_exit_code(2)

    def poll_workflow_status_blocking(self, workflow_id=0, success_status=20000):
        """ Polls the status of submitted workflow """
        poll_interval_seconds = 10
        if workflow_id == 0:
            workflow_id = self.args_output.workflow_id
        poll = True
        response_code = 0
        status_code = 0
        try:
            while poll:
                response_code, workflow = self.service.get_workflow_status(workflow_id)
                status_code = workflow.get("Status")
                self.display_status(workflow)
                self.set_exit_code(None, response_code, status_code)

                success = status_code == success_status
                failure = status_code == 50000 or status_code == 60000

                if success:
                    if self.download_output:
                        workflow["Message"] = "Downloading results"
                        self.display_status(workflow)
                        self.datatransfer.download_outputs(self.args_output.local_output_path)
                    self.datatransfer.clean_azure_cache()

                poll = not success and not failure

                if poll:
                    sleep(poll_interval_seconds)

        except Exception as exc:
            self.display_error(exc, response_code, status_code)

    def get_workflow_status(self):
        """ Gets the workflow status and sets the corresponding exit code """
        workflow_id = self.args_output.workflow_id
        status_code = 0
        response_code = 0
        try:
            response_code, workflow = self.service.get_workflow_status(workflow_id)
            status_code = workflow.get("Status", status_code)
            self.display_status(workflow, short=False)
            self.set_exit_code(None, None, status_code)

        except Exception as exc:
            self.display_error(exc, response_code, status_code)
            self.set_exit_code(1)

    def cancel_workflow(self):
        """ Cancels an existing workflow """
        workflow_id = self.args_output.workflow_id
        response_code = 0
        try:
            response_code, workflow = self.service.cancel_workflow_item(workflow_id)
            self.set_exit_code(None, response_code)
            response_code, workflow = self.service.get_workflow_status(workflow_id)
            self.display_status(workflow, short=False)
            self.set_exit_code(None, response_code, workflow.get("Status", 0))

        except Exception as exc:
            self.display_error(exc, response_code, None)
            self.set_exit_code(1)
            return

        if self.args_output.no_poll or workflow_id <= 0:
            return

        self.poll_workflow_status_blocking(0, 60000)

    def list_workflows(self):
        """ Lists existing workflows """
        response_code = 0
        try:
            response_code, workflow_data = self.service.get_workflow_list()
            print ""
            print "Workflow List"
            print "-------------"
            print "Total Count  : " + str(len(workflow_data))
            print ""
            for workflow in workflow_data:
                created_date = self.get_str_value(workflow, "CreatedDate")
                print "Workflow ID     : " + self.get_str_value(workflow, "Id")
                status_text = self.exit_status_by_workflow_status[workflow["Status"]][0]
                print "Status          : " + status_text
                print "Message         : " + self.get_str_value(workflow, "Message")
                print "Process         : " + self.get_str_value(workflow, "Process")
                print "Description     : " + self.get_str_value(workflow, "Description")
                print "Created Date    : " + created_date
                created_date_parts = created_date.split(".")
                created_date_object = datetime.strptime(created_date_parts[0], '%Y-%m-%dT%H:%M:%S')
                date_info = WorkflowExecutor.workflow_wall_clock_endtime(
                    self.get_str_value(workflow, "EndDate"),
                    created_date_object)
                print "End Date        : " + date_info[0]
                print "Wall clock time : %sh %sm %ss" % (date_info[1], date_info[2], date_info[3])
                print ""

            self.set_exit_code(None, response_code)

        except Exception as exc:
            self.display_error(exc, response_code, None)
            self.set_exit_code(1)


    def get_input_and_output_dict(self):
        """ gets the input dictionary with the service parameters """
        input_dic = dict()
        self.add_key_value(input_dic, "ACCOUNT",
                           self.args_output.input_storage_account_name, False)
        self.add_key_value(input_dic, "CONTAINER",
                           self.datatransfer.input_container, False)
        self.add_key_value(input_dic, "BLOBNAMES",
                           self.args_output.input_blob_name_1, True)
        self.add_key_value(input_dic, "BLOBNAMES",
                           self.args_output.input_blob_name_2, True)
        self.add_key_value(input_dic,
                           "BLOBNAMES_WITH_SAS",
                           self.datatransfer.create_input_blob_sas_url(
                               self.args_output.input_blob_name_1, self.args_output.sas_duration),
                           True)
        self.add_key_value(input_dic,
                           "BLOBNAMES_WITH_SAS",
                           self.datatransfer.create_input_blob_sas_url(
                               self.args_output.input_blob_name_2, self.args_output.sas_duration),
                           True)
        output_dic = dict()
        self.add_key_value(output_dic, "ACCOUNT",
                           self.args_output.output_storage_account_name, False)
        self.add_key_value(output_dic, "CONTAINER",
                           self.datatransfer.output_container, False)
        self.add_key_value(output_dic, "OVERWRITE",
                           str(self.args_output.output_overwrite).lower(), False)
        self.add_key_value(output_dic, "CONTAINER_SAS",
                           self.datatransfer.create_output_sas(self.args_output.sas_duration), False)
        self.add_key_value(output_dic, "OUTPUT_FILENAME_BASE",
                           self.args_output.output_filename_base, False)
        self.add_key_value(output_dic, "OUTPUT_INCLUDE_LOGFILES",
                           self.args_output.output_include_logfiles, False)

        return input_dic, output_dic
    def set_exit_code(self, result=None, response_code=None, workflow_status=None):
        """
        Sets exit code from the result, response code and/or workflow status.
        """
        #result always takes priority over the other params.
        if result is not None:
            self.current_exit_status = self.exit_status_by_result[result][1]
            return

        #failure for all edge conditions
        self.current_exit_status = 1000

        #only response code was provided
        if response_code in self.exit_status_by_response and workflow_status is None:
            self.current_exit_status = self.exit_status_by_response[response_code][1]
            return

        #failure in response takes priority when non-success
        if response_code != 200 and response_code in self.exit_status_by_response:
            self.current_exit_status = self.exit_status_by_response[response_code][1]
            return

        if workflow_status in self.exit_status_by_workflow_status:
            self.current_exit_status = self.exit_status_by_workflow_status[workflow_status][1]

    @classmethod
    def add_key_value(cls, dictionary, key, value, append_value):
        """adds a new value pair to the dictionary or appends to an existing value"""
        if append_value:
            if key in dictionary:
                dictionary[key] += value + ","
            else:
                dictionary[key] = value + ","
        else:
            dictionary[key] = value

    @classmethod
    def get_str_value(cls, dictionary, key, default=""):
        """gets a value from a dictionary if the key exists"""
        if not isinstance(dictionary, dict):
            return default
        if key in dictionary:
            value = dictionary[key]
            if value is not None:
                return str(value)
        return default
    