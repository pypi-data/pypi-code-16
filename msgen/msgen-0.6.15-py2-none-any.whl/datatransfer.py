# ----------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved. 
#  Licensed under the MIT License. See License.txt in the 
#  project root for license information.  If License.txt is 
#  missing, see https://opensource.org/licenses/MIT
# ----------------------------------------------------------

""" handles data transfer between local machine and blob storage """
import os
import subprocess
import msgen_cli.malibucommon as malibucommon
import msgen_cli.malibuazure as malibuazure

class AzureDataTransfer(object):

    """ Main class for working with workflows """
    def __init__(self, blobxfer_path,
                 storage_account_info,
                 azure_as_cache=False):
        """ Constructor """
        self.blobxfer_path = blobxfer_path
        self.storage_info = storage_account_info
        self.azure_as_cache = azure_as_cache
        self.input_container = self.storage_info.input.container
        self.output_container = self.storage_info.output.container
        self.output_container_sas = ""
        self.input_container_sas = ""

        if azure_as_cache:
            self.input_container = self.get_random_cache_container_name()
            self.output_container = self.get_random_cache_container_name()

    def get_random_cache_container_name(self):
        """ creates a container with a unique name """
        container_name = ""
        while True:
            container_name = "cache" + malibucommon.randomword(10)
            container_exists = malibuazure.container_exists(
                self.storage_info.input.name, self.storage_info.input.key, container_name)
            if not container_exists:
                break
        return container_name

    def parse_blobxfer_download_args(self, container, storage_virtual_dir, local_output):
        """ parses the blobxfer download command line parameters """
        print "Downloading from Azure Storage via Blobxfer..."
        print "Output path: " + local_output

        virtual_dir = "."
        if storage_virtual_dir != "" and storage_virtual_dir != None:
            virtual_dir = storage_virtual_dir

        args_template = ("{0} {1} {2} {3}"
                         " --download --no-computefilemd5"
                         " --remoteresource {5} --storageaccountkey {4}")
        blobxfer_download_args = args_template.format(
            self.blobxfer_path,
            self.storage_info.output.name,
            container,
            local_output,
            self.storage_info.output.key,
            virtual_dir)
        return blobxfer_download_args.split(" ")

    @classmethod
    def check_default_path(cls, path):
        """ checks if the default path from the os is expected """
        if path == "" or path is None:
            return "."
        elif path == "default":
            return os.getcwd()

        return path

    def parse_blobxfer_upload_args(self, container, storage_virtual_dir, input_path):
        """ parses the blobxfer upload command line parameters """
        virtual_dir = "."
        if storage_virtual_dir != "" and storage_virtual_dir != None:
            virtual_dir = storage_virtual_dir

        blobxfer_upload_template = ("{0} {1} {2} {3}"
                                    " --upload --no-computefilemd5"
                                    " --storageaccountkey {5} --collate {4}")
        blobxfer_upload_args = blobxfer_upload_template.format(self.blobxfer_path,
                                                               self.storage_info.input.name,
                                                               container,
                                                               input_path,
                                                               virtual_dir,
                                                               self.storage_info.input.key)
        return blobxfer_upload_args.split(" ")

    def upload_inputs(self,
                      *local_inputs):
        """ uploads local files to blobstorage using blobxfer """
        # Upload using blobxfer
        container_name = self.input_container

        for local_input in local_inputs:
            if local_input != "":
                blobxfer_upload_args = self.parse_blobxfer_upload_args(
                    container_name,
                    self.storage_info.input.virtual_dir,
                    local_input)

                blobxfer_return_code = subprocess.call(blobxfer_upload_args)

        return blobxfer_return_code, container_name

    def clean_azure_cache(self):
        """deletes the temporary containers if azure used as cache"""
        if self.azure_as_cache:
            malibuazure.delete_container(
                self.storage_info.input.name,
                self.storage_info.input.key,
                self.input_container)

            malibuazure.delete_container(
                self.storage_info.output.name,
                self.storage_info.output.key,
                self.output_container)

    def create_input_blob_sas_url(self, blob_name, sas_token_hours):
        """creates a sas token for the blob name"""
        if blob_name is None or blob_name == "":
            return ""

        sas_token = malibuazure.create_blob_sas_token(
            self.storage_info.input.name,
            self.storage_info.input.key,
            self.input_container,
            blob_name,
            sas_token_hours)

        return blob_name + '?' + sas_token

    def create_output_sas(self, sas_token_hours):
        """ Creates a container sas token in the output storage account """
        if self.output_container_sas is None or self.output_container_sas == "":
            sas_token = malibuazure.create_container_sas_token(
                self.storage_info.output.name,
                self.storage_info.output.key,
                self.output_container,
                sas_token_hours,
                True,
                False)

            self.output_container_sas = sas_token

        return self.output_container_sas

    def create_input_sas(self):
        """ Creates a container sas token in the input storage account """
        if self.input_container_sas is None or  self.input_container_sas == "":
            sas_token = malibuazure.create_container_sas_token(
                self.storage_info.input.name,
                self.storage_info.input.key,
                self.input_container,
                True)

            self.input_container_sas = sas_token

        return self.input_container_sas


    def download_outputs(self, local_output):
        """ downloads output files from blobstorage using blobxfer """
        local = AzureDataTransfer.check_default_path(local_output)

        output = "."
        output_path_name = self.storage_info.output.virtual_dir
        if output_path_name != "" and output_path_name != None:
            output = output_path_name

        return_code = 0

        args_list = self.parse_blobxfer_download_args(
            self.storage_info.output.container,
            output,
            local)

        return_code = subprocess.call(args_list)
        return return_code
