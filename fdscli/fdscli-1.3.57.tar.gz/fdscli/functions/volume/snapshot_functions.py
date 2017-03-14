# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import collections
import getpass
import json
import time
from collections import OrderedDict
from fdscli.functions.datetime_functions import DatetimeFunctions
from fdscli.model.fds_error import FdsError
from fdscli.model.volume.snapshot import Snapshot
from fdscli.model.volume.volume import Volume
from fdscli.plugins.abstract_plugin import AbstractPlugin
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.snapshot_policy_service import SnapshotPolicyService
from fdscli.services import response_writer
from fdscli.services import volume_service
from fdscli.utils.byte_converter import ByteConverter
from fdscli.utils.converters.volume.snapshot_converter import SnapshotConverter
from fdscli.utils.converters.volume.snapshot_policy_converter import SnapshotPolicyConverter
from fdscli.utils.converters.volume.volume_converter import VolumeConverter

class VolumeSnapshotFunctions(AbstractPlugin):
    '''Functions for the ``volume snapshot`` sub-command.
    '''
    
    def __init__(self, volume_client):
        AbstractPlugin.__init__(self)
        self.volume_client = volume_client
        self.datetime_functions = DatetimeFunctions()

    @property
    def datetime_functions(self):
        return self.__datetime_functions

    @datetime_functions.setter
    def datetime_functions(self, datetime_functions):
        self.__datetime_functions = datetime_functions

    @property
    def volume_client(self):
        return self.__volume_client

    @volume_client.setter
    def volume_client(self, volume_client):
        self.__volume_client = volume_client

    def create_snapshot(self, args):
        '''Create a snapshot for a volume
        '''
        volume_id = args[AbstractPlugin.pos_arg_str['volume_id']]
        volume = self.get_volume_client().get_volume(volume_id)

        if (volume is None):
            print("No volume found with the specified identification.\n")
            return

        snapshot = Snapshot()

        snapshot.name = args[AbstractPlugin.pos_arg_str['name']]
        snapshot.retention = args[AbstractPlugin.retention_str]
        snapshot.volume_id = volume.id
        
        response = self.volume_client.create_snapshot( snapshot )
        
        if isinstance(response, Snapshot):
            self.list_snapshots(args)

        return

    def filter_by_date(self, timestamp_filter, snapshots):
        '''Better would be to send the timestamp filter to the server and do the filtering there.
            TODO ^^^
        '''
        if len(timestamp_filter) == 0:
            return snapshots
        filtered_snapshots = []
        for snapshot in snapshots:
            if DatetimeFunctions.in_range(snapshot.created, timestamp_filter) is True:
                filtered_snapshots.append(snapshot)
        return filtered_snapshots

    def list_snapshots(self, args):
        '''List snapshots for this volume
        '''
        # Validate timestamp range before calling any web services
        timestamp_range = self.datetime_functions.validate_timestamp_filter(args)
        if isinstance(timestamp_range, FdsError):
            return

        volume_id = args[AbstractPlugin.pos_arg_str['volume_id']]
        response = self.volume_client.list_snapshots(volume_id)
        
        if isinstance( response, FdsError ):
            return 1
        
        if len(response) == 0:
            print("\nNo snapshots found for volume with ID " + volume_id)
            return

        filtered_response = self.filter_by_date(timestamp_range, response)

        if len(filtered_response) == 0:
            print "\nNo snapshots found for volume ID '{}' with date-time filter.".format(volume_id)

        #print it all out
        if "format" in args  and args[AbstractPlugin.format_str] == "json":
            
            j_snapshots = []
            
            for snapshot in filtered_response:
                j_snapshot = SnapshotConverter.to_json(snapshot)
                j_snapshot = json.loads( j_snapshot )
                j_snapshots.append( j_snapshot )
                
            response_writer.ResponseWriter.writeJson( j_snapshots )
        else:
            resultList = response_writer.ResponseWriter.prep_snapshot_for_table( self.session, filtered_response)
            response_writer.ResponseWriter.writeTabularData( resultList )

    def add_snapshot_command(self, subparser):
        '''
        Creates the parser for the ``volume snapshot`` sub-command.

        Parameters
        ----------
        :type subparser: ``argparse._SubParsersAction``
        :param subparser: parsers action
        '''
        msg = ("Create and manage volume snapshots.")
        __snapshot_parser = subparser.add_parser("snapshot", description=msg, help=msg)

        snapshot_subparser = __snapshot_parser.add_subparsers(title="subcommands",
            description="volume snapshot subcommands",
            help="description:")

        msg_for_create = ("Create a snapshot from a given volume.")
        __create = snapshot_subparser.add_parser("create", description=msg_for_create, help=msg_for_create)

        # Optional args
        __create.add_argument("-" + AbstractPlugin.retention_str, help=("The time (in seconds) that "
            "this snapshot will be retained.  0 = forever."), default=0, type=int)
        self.add_format_arg(__create)

        # Required positional arguments
        __create.add_argument(AbstractPlugin.pos_arg_str['name'], help="The snapshot name.")
        __create.add_argument(AbstractPlugin.pos_arg_str['volume_id'],
            help=("Create snapshot from the volume with this UUID."))

        __create.set_defaults( func=self.create_snapshot, format="tabular" )


        msg_for_list = ("List snapshots for a given volume.")
        __list = snapshot_subparser.add_parser("list", description=msg_for_list, help=msg_for_list)

        # Optional args
        self.add_format_arg(__list)
        self.datetime_functions.add_datetime_range_options(__list)

        # Required positional arguments
        __list.add_argument(AbstractPlugin.pos_arg_str['volume_id'],
            help=("List snapshots for the volume with this UUID."))

        __list.set_defaults( func=self.list_snapshots, format="tabular")

    def get_volume_client(self):
        '''
        '''        
        return self.__volume_client           

