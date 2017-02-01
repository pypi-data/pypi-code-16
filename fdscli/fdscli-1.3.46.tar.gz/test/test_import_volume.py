#
# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions
from fdscli.model.common.repository import Repository
from fdscli.model.volume.volume import Volume
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.volume_service import VolumeService
from fdscli.utils.converters.volume.volume_converter import VolumeConverter

def mock_post( session, url, data ):
    print url

def mock_get_url_preamble():
    return "http://localhost:7777/fds/config/v09"

class VolumeImportTest( BaseCliTest ):
    '''
    Test case for volume import. IS-A unittest.TestCase.
    '''
    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.volume_service.VolumeService.import_volume", side_effect=mock_functions.importVolume)
    def test_import_volume(self, mockImportVolume, mockTabular, mockPretty):
        '''
        The volume service calls are replaced by mock functions.

        Parameters
        ----------
        mockImportVolume (unittest.mock.MagicMock)
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''
        args = ["volume", "import", "newvol", "-s3_object_prefix=1/42/2016-04-04T00:00:01", 
            "-s3_bucket_name=xvolrepo", "-s3_access_key=ABCDEFG",
            "-s3_secret_key=/52/yrwhere", "-url=https://s3.amazon.com"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockImportVolume.call_count == 1

        volume_name = mockImportVolume.call_args[0][0]

        assert volume_name == "newvol"

        repo = mockImportVolume.call_args[0][1]

        assert repo.url == "https://s3.amazon.com"
        assert repo.bucket_name == "xvolrepo"
        assert repo.remote_om == None
        assert repo.new_volume_name == "newvol"
        assert repo.obj_prefix_key == "1/42/2016-04-04T00:00:01"
        assert repo.credentials.access_key_id == "ABCDEFG"
        assert repo.credentials.secret_key == "/52/yrwhere"

        print("test_import_volume passed.\n\n")

    '''
    Test case for volume import with a stored credential. IS-A unittest.TestCase.
    '''
    @patch("fdscli.services.volume_service.VolumeService.import_volume", side_effect=mock_functions.importVolume)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credential_by_key", side_effect=mock_functions.getNamedCredentialByKey)
    def test_import_volume_w_credential(self, mockGetCredential, mockImportVolume):
        '''
        The volume service calls are replaced by mock functions.

        Parameters
        ----------
        mockImportVolume (unittest.mock.MagicMock)
        mockGetCredential (unittest.mock.MagicMock)
        '''
        args = ["volume", "import", "newvol", "-s3_object_prefix=1/42/2016-04-04T00:00:01",
            "--credential=333333"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockImportVolume.call_count == 1
        volume_name = mockImportVolume.call_args[0][0]

        assert volume_name == "newvol"

        repo = mockImportVolume.call_args[0][1]

        assert repo.new_volume_name == "newvol"
        assert repo.obj_prefix_key == "1/42/2016-04-04T00:00:01"
       
        credential_digest = mockImportVolume.call_args[0][2]
        assert credential_digest == "333333"
 
        print("test_import_volume_w_credential passed.\n\n")

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.abstract_service.AbstractService.get_url_preamble", side_effect=mock_get_url_preamble)
    @patch("fdscli.services.rest_helper.RESTHelper.post", side_effect=mock_post)
    @patch("fdscli.services.volume_service.VolumeService.get_volume", side_effect=mock_functions.getVolume)
    def test_service(self, mockServiceGetVolume, mockServicePost, mockUrlPreamble, mockTabular, mockPretty):
        '''
        Directly tests the real VolumeService.import_volume.

        Parameters
        ----------
        mockServiceGetVolume (unittest.mock.MagicMock)
        mockServicePost (unittest.mock.MagicMock) : Replace REST helper post() with mock empty
        mockUrlPreamble (unittest.mock.MagicMock) : Returns the string to prepend for POST Url
        mockTabular (unittest.mock.MagicMock)
        mockPretty (unittest.mock.MagicMock)
        '''
        new_volume_name = "import1"

        repo = Repository()
        repo = Repository();
        repo.url = "https://s3.amazon.com"
        repo.bucket_name = "xvolrepo"
        repo.remote_om = None
        repo.credentials.access_key_id = "ABCDEFG"
        repo.credentials.secret_key = "/52/yrwhere"

        session = FdsAuth()
        service = VolumeService(session)
        service.import_volume(new_volume_name, repo)

        # The service import volume is a url producer
        assert mockServicePost.call_count == 1
        url = mockServicePost.call_args[0][1]
        assert url == "http://localhost:7777/fds/config/v09/volumes/imports/s3"
        body = mockServicePost.call_args[0][2]
        print body

        print("VolumeImportTest.test_service ok.\n\n")

