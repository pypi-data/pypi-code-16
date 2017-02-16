# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#

from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions
from fdscli.model.fds_error import FdsError
from fdscli.model.volume.snapshot import Snapshot
from fdscli.services import volume_service
from fdscli.utils.converters.volume.snapshot_converter import SnapshotConverter


def mock_list_snapshots(volume_id):
    '''Request list of snapshot for a given volume.

    Parameters
    ----------
    :type volume_id: int
    :param volume_id: Unique identifier for a volume

    Returns
    -------
    :type ``model.FdsError`` or list(``Snapshot``)
    '''
    snapshots = []
    snapshot = Snapshot()

    snapshot.name = 'snap1'
    snapshot.retention = '0'
    snapshot.volume_id = '11'

    snapshots.append(snapshot)
    return snapshots

class VolumeSnapshotTest( BaseCliTest ):
    '''Tests plugin and service client functionality for ``volume snapshot`` command.

    IS-A unittest.TestCase.
    '''
    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.volume_service.VolumeService.list_snapshots", side_effect=mock_list_snapshots)
    def test_snapshot_list(self, mock_list_snaps, mockTabular, mockPretty):
        '''Tests the volume plugin for 'volume safeguard'.
        The subscription service calls are replaced by mock functions.

        Parameters
        ----------
        :type mock_list_snaps: ``unittest.mock.MagicMock``
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''
        args = ["volume", "snapshot", "list", "11"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mock_list_snaps.call_count == 1

        volume_id = mock_list_snaps.call_args[0][0]
        assert volume_id == '11'

        assert mock_list_snaps.call_count == 1
        print("test_snapshot_list.\n\n")

    @patch( "fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.findVolumeById )
    @patch( "fdscli.services.volume_service.VolumeService.list_snapshots", side_effect=mock_functions.listSnapshots )
    @patch( "fdscli.services.volume_service.VolumeService.create_snapshot", side_effect=mock_functions.createSnapshot)
    def test_snapshot_create(self, mockCreate, mockList, mockFindId ):
        '''
        basic snapshot creation
        '''
        args = ["volume", "snapshot", "create", "MySnap", "100"]

        self.callMessageFormatter(args)

        self.cli.run( args )

        assert mockCreate.call_count == 1
        assert mockList.call_count == 1
        assert mockFindId.call_count == 1

        snapshot = mockCreate.call_args[0][0]

        assert snapshot.volume_id == "100"
        assert snapshot.name == "MySnap"

        print("Snapshot created successfully.")

