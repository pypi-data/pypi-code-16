# ----------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved. 
#  Licensed under the MIT License. See License.txt in the 
#  project root for license information.  If License.txt is 
#  missing, see https://opensource.org/licenses/MIT
# ----------------------------------------------------------

"""File for all argument parsing"""
import sys
import os
import os.path
import argparse
import re
from collections import namedtuple

class MaxLengthValidator(argparse.Action):
    def __init__(self, option_strings, max_length, *args, **kwargs):
        self.max_length = max_length
        return super(MaxLengthValidator, self).__init__(option_strings, *args, **kwargs)
    def __call__(self, parser, namespace, values, option_string = None):
        if (values is not None and len(values) > self.max_length):
            print "Maximum length for the '{0}' field is {1}. Your value will be truncated.".format(self.dest, self.max_length)
            values = values[:self.max_length]
        setattr(namespace, self.dest, values)

class PositiveIntValidator(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        positive = int(values)
        if positive <= 0:
            raise ValueError("Value of {0} should be positive.".format(self.dest))
        setattr(namespace, self.dest, positive)

_badInputBlobChars = re.compile("[^A-Za-z0-9._/-]")
_badOutputBaseNameChars = re.compile("[^A-Za-z0-9._-]")

class BlobNameValidator(argparse.Action):
    def __init__(self, option_strings, regex, isinput, *args, **kwargs):
        self.regex = regex
        self.isinput = isinput
        return super(BlobNameValidator, self).__init__(option_strings, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string = None):
        # Name length 1-1024 (https://docs.microsoft.com/en-us/azure/guidance/guidance-naming-conventions#naming-rules-and-restrictions)
        # Characters: alphanumeric, dot, dash, and underscore
        if values is not None and len(values) > 0:
            if len(values) > 1024:
                raise ValueError("Length of {0} should be 1-1024 characters.".format(self.dest))
            if bool(self.regex.search(values)):
                error = "{0} should contain only alphanumeric characters, dot, dash, underscore."
                if self.isinput:
                    error = error[:len(error)-1] + ", slash."
                raise ValueError("{0} should contain only alphanumeric characters, dot, dash, underscore.".format(self.dest))
        setattr(namespace, self.dest, values)

class ArgsOutput(object):
    """Class that contains all arguments passed to app"""
    def __init__(self):
        """Constructor"""

        self.args_file = ""
        self.subscription_key = ""
        self.command = ""
        self.workflow_id = ""
        self.process_name = ""
        self.process_args = ""
        self.description = ""

        self.input_storage_account_type = ""
        self.input_storage_account_name = ""
        self.input_storage_account_key = ""
        self.input_storage_account_container = ""
        self.input_storage_account_vdir = ""
        #self.input_storage_account_container_sas = ""
        self.input_blob_name_1 = ""
        self.input_blob_name_2 = ""
        
        self.output_storage_account_type = ""
        self.output_storage_account_name = ""
        self.output_storage_account_key = ""
        self.output_storage_account_container = ""
        self.output_storage_account_vdir = ""
        #self.output_storage_account_container_sas = ""
        self.output_overwrite = False
        self.output_filename_base = ""
        self.output_include_logfiles = True
        self.sas_duration = 0

        self.local_input_1 = ""
        self.local_input_2 = ""
        self.local_output_path = ""
        self.blobxfer_path = ""
        self.azure_as_cache_mode = False

        self.api_url_base = ""
        self.no_poll = False
        self.debug_mode = False
        self.workflow_class = ""

        self.input_dictionary = dict()
        self.output_dictionary = dict()

    def get_file_path(self):
        """Parses path considering Linux and Windows scenarios"""
        file_path = self.args_file
        #if not file_path.strip():
        #    return None
        file_path = self.args_file.strip()
        if os.path.isfile(file_path):
            # file exists
            return file_path
        else:
            # file_path is non-empty but not a full filepath
            slash = "/"
            if os.name == "nt":
                #Windows
                slash = "\\"
            # Assume file with no directory refers to current directory
            if slash not in file_path:
                file_path = os.path.dirname(os.path.realpath(sys.argv[0])) + slash + file_path
                if os.path.isfile(file_path):
                    return file_path

            # Nothing specified, try default config.txt
            file_path = os.path.dirname(os.path.realpath(sys.argv[0])) + slash + "config.txt"
            if os.path.isfile(file_path):
                return file_path
            else:
                return None

    def parse_args_from_file(self, parser = None, omit_arguments = None):
        """Iterates through all arguments found in the file"""
        parser = parser if parser else ArgsOutput.create_parser()
        omit_arguments = omit_arguments if omit_arguments else []

        file_path = self.get_file_path()
        
        if file_path:
            arglist = []
            with open(file_path) as argsfile:
                lines = argsfile.readlines()
                for line in lines:
                    if line is None or line == "" or line.startswith("#"):
                        continue
                    columns = line.split(':', 1)
                    if len(columns) == 2:
                        key = "-" + columns[0].strip()
                        value = columns[1].strip()
                        arglist.extend([key, value])
            # parse the config file applying all validation rules to its contents
            for key, value in vars(parser.parse_args(arglist)).iteritems():
                if key not in omit_arguments:
                    self.set_args_value(key, value)

    def set_args_value(self, key, value):
        """Sets class properties from key value pair"""
        if value is None: # Do not override defaults
            return
        if str(value).lower() == "true" or str(value).lower() == "false":
            bool_value = str(value).lower() == "true"
            setattr(self, key, bool_value)
            return
        if key == "command":
            setattr(self, key, str(value).upper())
            return

        setattr(self, key, value)

    def parse_args_from_command_line(self):
        """Parses arguments from command line and settings file if present"""
        parser = ArgsOutput.create_parser()
        parser.add_argument(
            "-f",
            help="""Specifies a settings file to look for
                    command-line arguments.
                    Command-line arguments will take precedence
                    and override the file.""",
            required=False)
        args = vars(parser.parse_args())

        arg_name = "f"
        if args[arg_name] != None:
            self.args_file = str(args[arg_name]).strip()

        self.parse_args_from_file(parser, [arg_name])

        # manually parse each arg and override values from settings file
        for key, value in args.iteritems():
            self.set_args_value(key, value)

    def validate(self):
        """Checks if required arguments provided"""
        if not (self.api_url_base and self.subscription_key):
            return "-api_url_base and -subscription_key are required for all commands"
        if not self.command:
            return "-command is required and should be one of SUBMIT, GETSTATUS, CANCEL, LIST"
        if self.command == "SUBMIT":
            return self.validate_submit()
        elif self.command in ["GETSTATUS", "CANCEL"] and not self.workflow_id:
            return "-workflow_id is required for getting a status of or canceling a workflow"
        else:
            return None

    def validate_submit(self):
        required = ["process_name",
                    "input_storage_account_container", "input_storage_account_key", "input_storage_account_name", "input_storage_account_type",
                    "output_storage_account_container", "output_storage_account_key", "output_storage_account_name", "output_storage_account_type"]
        first_missing = next((a for a in required if not vars(self)[a]), None)
        if first_missing:
            return "-{0} is required for submitting workflows"

        if not (self.input_blob_name_1 or self.input_blob_name_2):
            return "At least one of -input_blob_name_1 and -input_blob_name_2 is required for submitting workflows"

        return None            

    def get_storage_accounts_info(self):
        """
        Returns a named tuple with the input and output storage information
        """
        AccountInfo = namedtuple(
            "AccountInfo",
            "name key container virtual_dir")
        StorageInfo = namedtuple(
            "StorageInfo",
            "input output")
        storage_info = StorageInfo(
            AccountInfo(
                self.input_storage_account_name,
                self.input_storage_account_key,
                self.input_storage_account_container,
                self.input_storage_account_vdir),
            AccountInfo(
                self.output_storage_account_name,
                self.output_storage_account_key,
                self.output_storage_account_container,
                self.output_storage_account_vdir))

        return storage_info

    @staticmethod
    def create_parser():
        """Creates a parser for arguments shared between the configuration file and command line options"""
        parser = argparse.ArgumentParser(
            description="""A command-line tool to run genomics processes on
                        the Microsoft Genomics platform.
                        For example usage, please see https://pypi.python.org/pypi/msgen""")

        parser.add_argument("-command", help="One of SUBMIT, LIST, GETSTATUS, CANCEL.", required=False)
        parser.add_argument("-workflow_id", help="Workflow ID return after submission.", required=False)

        parser.add_argument("-process_name",
                            help="Name of the genomics process.",
                            required=False)
        parser.add_argument("-process_args",
                            help="Arguments for the genomics process.", required=False)
        parser.add_argument("-description",
                            help="Workflow description.", required=False, action=MaxLengthValidator, max_length=500)

        parser.add_argument("-input_storage_account_type", help="Always use AZURE_BLOCK_BLOB.", required=False, default="AZURE_BLOCK_BLOB")
        parser.add_argument("-input_storage_account_name", help="Your storage account name for input files.", required=False)
        parser.add_argument("-input_storage_account_key", help="Input storage account key.", required=False)
        parser.add_argument("-input_storage_account_container", help="Input files container.", required=False)
        parser.add_argument("-input_blob_name_1", help="First blob name.", required=False, action=BlobNameValidator,
                            regex=_badInputBlobChars, isinput=True)
        parser.add_argument("-input_blob_name_2", help="Second blob name.", required=False, action=BlobNameValidator,
                            regex=_badInputBlobChars, isinput=True)

        parser.add_argument("-output_storage_account_type", help="Always use AZURE_BLOCK_BLOB.", required=False, default="AZURE_BLOCK_BLOB")
        parser.add_argument("-output_storage_account_name", help="Your storage account name for output files.", required=False)
        parser.add_argument("-output_storage_account_key", help="Output storage account key.", required=False)
        parser.add_argument("-output_storage_account_container", help="Output files container.", required=False)
        parser.add_argument("-output_overwrite", help="Whether to overwrite blobs in the output container.", required=False)
        parser.add_argument("-output_filename_base", help="Output file name base for the genomics processor.", required=False,
                            action=BlobNameValidator, regex=_badOutputBaseNameChars, isinput=False)
        parser.add_argument("-output_include_logfiles", help="Whether to upload log files along with results.", required=False)

        parser.add_argument("-no_poll", help="Whether to continue polling workflow status after submission.", required=False)
        parser.add_argument("-api_url_base", help="Microsoft Genomics API URL.", required=False)
        parser.add_argument("-subscription_key", help="Your Microsoft Genomics subscription key.", required=False)

        parser.add_argument("-sas_duration",
                            help="SAS token duration for input/output blobs, in hours", required=False, action=PositiveIntValidator, default=24)

        # Hide help messages for internal details
        parser.add_argument("-workflow_class", help=argparse.SUPPRESS, required=False)

        # Deprecate blobxfer-related arguments by hiding their help messages
        parser.add_argument("-blobxfer_path", help=argparse.SUPPRESS, required=False)
        parser.add_argument("-input_storage_account_vdir", help=argparse.SUPPRESS, required=False)
        parser.add_argument("-output_storage_account_vdir", help=argparse.SUPPRESS, required=False)
        parser.add_argument("-local_input_1", help=argparse.SUPPRESS, required=False)
        parser.add_argument("-local_input_2", help=argparse.SUPPRESS, required=False)
        parser.add_argument("-local_output_path", help=argparse.SUPPRESS, required=False)
        parser.add_argument("-azure_as_cache_mode", help=argparse.SUPPRESS, required=False)
        return parser
