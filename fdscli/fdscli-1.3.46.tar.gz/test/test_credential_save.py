# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.common.s3credentials import S3Credentials
from fdscli.model.volume.volume import Volume
from fdscli.utils.converters.volume.volume_converter import VolumeConverter

def mock_create(named_credential):
    return named_credential

class TestCredentialSave(BaseCliTest):
    '''Tests plugin and service client functionality for ``credential save`` commands.

    IS-A unittest.TestCase.
    '''
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.create_named_credential",
        side_effect=mock_create)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credentials",
        side_effect=mock_functions.empty)
    def test_save_f1(self, mockGet, mockCreate):
        '''Tests the credential plugin for ``credential save f1``.

        A parser for the command is created in the NamedCredentialPlugin.
        All service client calls are mocked.

        Parameters
        ----------
        :type mockGet: ``unittest.mock.MagicMock``
        :type mockCreate: ``unittest.mock.MagicMock``
        '''
        print("Plugin test: credential save f1")

        # It is okay for the https port to be 7777 here. There is a possibility that customer
        # changed platform.conf to set that up.
        args = ["credential", "save", "f1", "name1", "https", "hannah.reid", "secret",
            "localhost", "7777"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockCreate.call_count == 1
        assert mockGet.call_count == 1

        credential = mockCreate.call_args[0][0]

        assert credential.hostname == "localhost"
        assert credential.name == "name1"
        assert credential.url == "https://hannah.reid:secret@localhost:7777"
        assert credential.bucketname == None
        assert credential.password == "secret"
        assert credential.port == 7777
        assert credential.username == "hannah.reid"

        print("PASSED.\n")

    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.create_named_credential",
        side_effect=mock_create)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credentials",
        side_effect=mock_functions.empty)
    def test_save_f1_https(self, mockGet, mockCreate):
        '''Tests the credential plugin for ``credential save f1 https``.

        A parser for the command is created in the NamedCredentialPlugin.
        All service client calls are mocked.

        Parameters
        ----------
        :type mockGet: ``unittest.mock.MagicMock``
        :type mockCreate: ``unittest.mock.MagicMock``
        '''
        print("Plugin test: credential save f1 https")

        # Tests port default for https protocol

        args2 = ["credential", "save", "f1", "name2", "https", "hannah.reid", "secret",
            "localhost"]

        self.callMessageFormatter(args2)
        self.cli.run(args2)
        assert mockCreate.call_count == 1
        assert mockGet.call_count == 1

        credential2 = mockCreate.call_args[0][0]

        assert credential2.hostname == "localhost"
        assert credential2.name == "name2"
        assert credential2.url == "https://hannah.reid:secret@localhost:7443"
        assert credential2.bucketname == None
        assert credential2.password == "secret"
        assert credential2.port == 7443
        assert credential2.username == "hannah.reid"

        print("PASSED.\n")

    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.create_named_credential",
        side_effect=mock_create)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credentials",
        side_effect=mock_functions.empty)
    def test_save_f1_http(self, mockGet, mockCreate):
        '''Tests the credential plugin for ``credential save f1 http``.

        A parser for the command is created in the NamedCredentialPlugin.
        All service client calls are mocked.

        Parameters
        ----------
        :type mockGet: ``unittest.mock.MagicMock``
        :type mockCreate: ``unittest.mock.MagicMock``
        '''
        print("Plugin test: credential save f1 http")

        # Tests port default for http protocol

        args3 = ["credential", "save", "f1", "name3", "http", "hannah.reid", "secret",
            "localhost"]

        self.callMessageFormatter(args3)
        self.cli.run(args3)
        assert mockCreate.call_count == 1
        assert mockGet.call_count == 1

        credential3 = mockCreate.call_args[0][0]

        assert credential3.hostname == "localhost"
        assert credential3.name == "name3"
        assert credential3.url == "http://hannah.reid:secret@localhost:7777"
        assert credential3.bucketname == None
        assert credential3.password == "secret"
        assert credential3.port == 7777
        assert credential3.username == "hannah.reid"

        print("PASSED.\n")

    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.create_named_credential",
        side_effect=mock_create)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credentials",
        side_effect=mock_functions.empty)
    def test_save_s3(self, mockGet, mockCreate):
        '''Tests the credential plugin for ``credential save s3``.

        A parser for the command is created in the NamedCredentialPlugin.
        All service client calls are mocked.

        Parameters
        ----------
        :type mockGet: ``unittest.mock.MagicMock``
        :type mockCreate: ``unittest.mock.MagicMock``
        '''
        print("Plugin test: credential save s3")

        args = ["credential", "save", "s3", "credentialNameS3", "https://s3.amazon.com",
            "xvolrepo", "ABCDEFG", "/52/yrwhere"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockCreate.call_count == 1
        assert mockGet.call_count == 1

        credential = mockCreate.call_args[0][0]

        assert credential.name == "credentialNameS3"
        assert credential.url == "https://s3.amazon.com"
        assert credential.bucketname == "xvolrepo"
        assert credential.s3credentials.access_key_id == "ABCDEFG"
        assert credential.s3credentials.secret_key == "/52/yrwhere"

        print("PASSED.\n")

