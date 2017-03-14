#
# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.volume.volume import Volume
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.volume_service import VolumeService
from fdscli.utils.converters.common.repository_converter import RepositoryConverter
from fdscli.utils.converters.volume.volume_converter import VolumeConverter

def mock_post( session, url, data ):
    print url

def mock_get_url_preamble():
    return "http://localhost:7777/fds/config/v09"

def mockGetNamedCredential(key):
    credential = NamedCredential(digest="ABCDEF", user_id=1, name="fakef1")
    credential.url = "https://hannah.reid:secret@localhost:7777"
    credential.protocol = "https"
    credential.username = "hannah.reid"
    credential.password = "secret"
    credential.hostname = "localhost"
    credential.port = 7777
    return credential

def mock_replicate(remote_volume, credential_key, snapshot_id, from_last_clone_remote):
    return "{code: 202, description: \'accepted\'}"

class VolumeReplicateTest( BaseCliTest ):
    '''Tests plugin and service client functionality for 'volume replicate' command.

    IS-A unittest.TestCase.
    '''
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credential_by_key",
        side_effect=mockGetNamedCredential)
    @patch("fdscli.services.volume_service.VolumeService.replicate_snapshot", side_effect=mock_replicate)
    @patch("fdscli.services.safeguard.safeguard_task_client.SafeGuardTaskClient.list_tasks_by_volume",
        side_effect=mock_functions.empty_one)
    def test_volume_replicate(self, mock_tasks, mock_replicate_volume, mock_credential, mock_volume):
        '''Tests the volume plugin for 'volume replicate'.

        The  service calls are replaced by mock functions.

        Parameters
        ----------
        :type mock_tasks: ``unittest.mock.MagicMock``
        :type mock_replicate_volume: ``unittest.mock.MagicMock``
        :type mock_credential: ``unittest.mock.MagicMock``
        :type mock_volume: ``unittest.mock.MagicMock``
        '''
        args = ["volume", "replicate", "-c=cred", "-snapshot_id=400", "-volume_id=3", "-name=replica1"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mock_replicate_volume.call_count == 1

        remote_volume = mock_replicate_volume.call_args[0][0]
        assert remote_volume.remote_om_url == "https://hannah.reid:secret@localhost:7777"
        assert remote_volume.source_volume_name == "FakeVol"
        assert remote_volume.volume.name == "replica1"

        credential_key = mock_replicate_volume.call_args[0][1]
        assert credential_key == "ABCDEF"

        snapshot_id = mock_replicate_volume.call_args[0][2]
        assert snapshot_id == 400L

        from_last_clone_remote = mock_replicate_volume.call_args[0][3]
        assert from_last_clone_remote == True

        print("test_volume_replicate passed.\n\n")

