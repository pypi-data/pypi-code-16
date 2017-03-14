# Copyright 2017 Formation Data Systems, Inc. All Rights Reserved.
#
from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions

def mock_get(cleartext=None):
    return []

class TestCredentialList(BaseCliTest):
    '''Tests plugin and service client functionality for ``credential list`` commands.

    IS-A unittest.TestCase.
    '''
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credentials",
        side_effect=mock_get)
    def test_list(self, mockGet):
        '''Tests the credential plugin for ``credential list``.

        A parser for the command is created in the NamedCredentialPlugin.
        All service client calls are mocked.

        Parameters
        ----------
        :type mockGet: ``unittest.mock.MagicMock``
        '''
        print("Plugin test: credential list")

        args = ["credential", "list"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockGet.call_count == 1

        cleartext = mockGet.call_args[0][0]
        assert not cleartext

        ''' now with cleartext (non-obfuscated) '''
        args = ["credential", "list", "-cleartext"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockGet.call_count == 2
        
        cleartext = mockGet.call_args[0][0]
        assert cleartext
 
        print("PASSED.\n")
