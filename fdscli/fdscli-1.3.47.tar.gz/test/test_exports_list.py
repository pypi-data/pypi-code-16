# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.common.s3credentials import S3Credentials
from fdscli.model.volume.volume import Volume
from fdscli.utils.converters.volume.volume_converter import VolumeConverter

def mockGetNamedCredential(key):
    credential = NamedCredential()
    credential.s3credentials = S3Credentials()
    credential.bucketname = "xvolrepo"
    credential.s3credentials.access_key_id = "ABCDEFG"
    credential.s3credentials.secret_key = "/52/yrwhere"
    credential.url = "https://s3.amazon.com"
    return credential

class TestExportsList( BaseCliTest ):
    '''
    Test case for listing exported volumes in a bucket. IS-A unittest.TestCase.
    '''
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credential_by_key",
        side_effect=mockGetNamedCredential)
    @patch("fdscli.services.volume_service.VolumeService.list_exports_in_bucket", side_effect=mock_functions.listExports)
    def test_list_exports(self, mockListExportsService, mockGetNamedCredential):
        '''
        The volume service calls are replaced by mock functions.

        Parameters
        ----------
        mockListExportsService (unittest.mock.MagicMock)
        mockGetNamedCredential (unittest.mock.MagicMock)
        '''
        args = ["exports", "list", "-s3_access_key=ABCDEFG", "-s3_secret_key=/52/yrwhere",
            "-url=https://s3.amazon.com", "xvolrepo"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockListExportsService.call_count == 1

        repo = mockListExportsService.call_args[0][0]

        assert repo.url == "https://s3.amazon.com"
        assert repo.bucket_name == "xvolrepo"
        assert repo.remote_om == None
        assert repo.credentials.access_key_id == "ABCDEFG"
        assert repo.credentials.secret_key == "/52/yrwhere"

        # Again, using a named credential
        args = ["exports", "list", "-c=cred"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockListExportsService.call_count == 2
        assert mockGetNamedCredential.call_count == 1

        repo = mockListExportsService.call_args[0][0]

        assert repo.url == "https://s3.amazon.com"
        assert repo.bucket_name == "xvolrepo"
        assert repo.remote_om == None
        assert repo.credentials.access_key_id == "ABCDEFG"
        assert repo.credentials.secret_key == "/52/yrwhere"

        print("test_list_exports passed.\n\n")

    def mock_in_range(timestamp, datetime_range):
        '''Filters out dates prior to 1980
        '''
        if long(timestamp) < 315532800L: # 1980-01-01 GMT
            return False
        return True

    @patch("fdscli.functions.datetime_functions.DatetimeFunctions.in_range", side_effect=mock_in_range)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credential_by_key",
        side_effect=mockGetNamedCredential)
    @patch("fdscli.services.volume_service.VolumeService.list_exports_in_bucket", side_effect=mock_functions.listExports)
    def test_filtered_list(self, mockListExportsService, mockGetNamedCredential, mock_in_range):
        '''Validates calls to filter list of exports.

        The volume service calls are replaced by mock functions.

        Parameters
        ----------
        :type mockListExportsService: ``unittest.mock.MagicMock``
        :type mockGetNamedCredential: ``unittest.mock.MagicMock``
        :type mock_in_range: ``unittest.mock.MagicMock``
        '''
        args = ["exports", "list", "-c=foo", "-bd=1980-01-01", "-ed=2016-11-01"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockListExportsService.call_count == 1

        repo = mockListExportsService.call_args[0][0]

        assert repo.url == "https://s3.amazon.com"
        assert repo.bucket_name == "xvolrepo"
        assert repo.remote_om == None
        assert repo.credentials.access_key_id == "ABCDEFG"
        assert repo.credentials.secret_key == "/52/yrwhere"

        assert mock_in_range.call_count == 4
        timestamp_range = mock_in_range.call_args[0][1]
        assert len(timestamp_range) == 2
        assert timestamp_range[0] == 315532800 # 1980-01-01 GMT
        print timestamp_range
        print("test_filtered_list passed.\n\n")
