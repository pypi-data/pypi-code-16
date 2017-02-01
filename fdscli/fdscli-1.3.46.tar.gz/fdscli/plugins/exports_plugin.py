# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import argparse
import collections
import datetime
import json
from fdscli.functions.datetime_functions import DatetimeFunctions
from fdscli.model.volume.remote_volume import RemoteVolume
from fdscli.model.volume.volume import Volume
from fdscli.utils.converters.volume.exported_volume_converter import ExportedVolumeConverter
from .abstract_plugin import AbstractPlugin
from fdscli.utils.converters.volume.snapshot_policy_converter import SnapshotPolicyConverter
from fdscli.model.fds_error import FdsError
from fdscli.services import volume_service
from fdscli.services import response_writer
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.subscription.named_credential_client import NamedCredentialClient
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.common.s3credentials import S3Credentials
from fdscli.model.common.repository import Repository
from fdscli.utils.byte_converter import ByteConverter

class ExportsPlugin(AbstractPlugin):
    '''
    Provides management for exported (archive) volumes.

    Currently supports listing only.

    Attributes
    ----------
    :type _ExportsPlugin__volume_service: ``services.VolumeService``
    :attr _ExportsPlugin__volume_service: Low-level API for HTTP volumes API

    :type _ExportsPlugin__named_credential_client: ``services.subscription.NamedCredentialClient``
    :attr _ExportsPlugin__named_credential_client: Low-level API for HTTP named_credentials API

    :type _ExportsPlugin__datetime_functions: ``functions.DatetimeFunctions``
    :type _ExportsPlugin__parser: ``argparse.ArgumentParser``
    :type _ExportsPlugin__subparser: ``argparse._SubParsersAction``
    '''
    def __init__(self):
        AbstractPlugin.__init__(self)

    def build_parser(self, parentParser, session):
        '''
        @see: AbstractPlugin

        Parameters
        ----------
        parentParser (argparse.Action)
        session (services.FdsAuth)
        '''
        self.session = session
        
        if not self.session.is_allowed( FdsAuth.VOL_MGMT ):
            return

        self.__volume_service = volume_service.VolumeService( self.session )
        self.__named_credential_client = NamedCredentialClient( self.session )

        self.__datetime_functions = DatetimeFunctions()

        msg = ("Exported (archive) volume management.")
        self.__parser = parentParser.add_parser("exports", description=msg, help=msg)
        self.__subparser = self.__parser.add_subparsers( help="Available sub-commands")

        # Other operations may eventually make sense for exports, like cleaning or deleting.
        self.add_command_list( self.__subparser )

    def detect_shortcut(self, args):
        '''
        @see: AbstractPlugin
        '''        
        return None
        
    def add_command_list(self, subparser):
        '''
        Creates the parser for the ``exports list`` command.

        Parameters
        ----------
        :type subparser: ``argparse._SubParsersAction``
        :param subparser: parsers action
        '''
        msg_for_list = ("List exported volumes in an existing bucket. Specify a named credential "
            "for bucket access, or specify the bucket access arguments individually.")
        __parserForList = subparser.add_parser( "list", description=msg_for_list, help=msg_for_list)

        # Optional args
        self.add_format_arg(__parserForList)
        __parserForList.add_argument("-c", "--credential", help=("A named credential ID or name. "
            "Manage named credentials using the \'credential\' command."))
        self.__datetime_functions.add_datetime_range_options(__parserForList)

        __parserForList.add_argument("BUCKET_NAME", nargs='?', help=("An already existing bucket. "
            "The BUCKET_NAME and bucket access arguments are not used if a named credential is specified."))

        groupForS3Access = __parserForList.add_argument_group('bucket access arguments')

        groupForS3Access.add_argument( "-" + AbstractPlugin.s3_access_key_str, help="S3 access key")
        groupForS3Access.add_argument( "-" + AbstractPlugin.s3_secret_key_str, help="S3 secret key")
        groupForS3Access.add_argument( "-" + AbstractPlugin.url_str, help=(
            "The URL where the bucket resides. For Formation, a value like "
            "'https://us-east.formationds.com'. For AWS, a value like "
            "'https://s3-us-west-2.amazonaws.com'."))

        __parserForList.set_defaults(func=self.list_exports, format="tabular")

    def get_volume_service(self):
        return self.__volume_service           

    def get_named_credential_client(self):
        return self.__named_credential_client

    def filter_by_date(self, timestamp_filter, exports):
        '''Better would be to send the timestamp filter to the server and do the filtering there.
            TODO ^^^
        '''
        if len(timestamp_filter) == 0:
            return exports
        filtered_exports = []
        for export in exports:
            if DatetimeFunctions.in_range(export.creation_time, timestamp_filter) is True:
                filtered_exports.append(export)
        return filtered_exports

    def list_exports(self, args):
        '''
        List all available exports in a given bucket.
        '''
        # Validate timestamp range before calling any web services
        timestamp_range = self.__datetime_functions.validate_timestamp_filter(args)
        if isinstance(timestamp_range, FdsError):
            return

        bucket_name = None
        if "BUCKET_NAME" in args and args["BUCKET_NAME"] is not None:
            bucket_name = args["BUCKET_NAME"]

        credential_key = None
        if "credential" in args and args["credential"] is not None:
            credential_key = args["credential"]

        repository = Repository()
        if credential_key is None:
            repository.bucket_name = bucket_name
            repository.credentials.access_key_id = args[AbstractPlugin.s3_access_key_str]
            repository.credentials.secret_key = args[AbstractPlugin.s3_secret_key_str]
            repository.url = args[AbstractPlugin.url_str]
        else:
            repository = self.get_named_credential_client().get_s3_repository(credential_key)
            if (repository is None or not isinstance(repository, Repository)):
                return

        if repository.bucket_name is None:
            print("BUCKET_NAME is required.\n")
            return

        response = self.get_volume_service().list_exports_in_bucket(repository)

        if isinstance(response, FdsError):
            return

        if isinstance(response, collections.Iterable):
            if (len(response) == 0):
                print("No exported volumes found for bucket '{}'.\n".format(repository.bucket_name))
                return

        filtered_response = self.filter_by_date(timestamp_range, response)

        #print it all out
        if "format" in args  and args[AbstractPlugin.format_str] == "json":

            j_exports = []

            for export in filtered_response:
                j_export = ExportedVolumeConverter.to_json(export)
                j_export = json.loads( j_export )
                j_exports.append( j_export )

            response_writer.ResponseWriter.writeJson( j_exports )
        else:
            resultList = response_writer.ResponseWriter.prep_exports_for_table( self.session, filtered_response)
            response_writer.ResponseWriter.writeTabularData( resultList )  
