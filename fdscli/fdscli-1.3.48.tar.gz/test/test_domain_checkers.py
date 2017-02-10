from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions

class TestDomainCheckers(BaseCliTest):
    '''
    Created on Jul 26, 2016

    @author: Neil
    '''

    @patch( "fdscli.services.volume_service.VolumeService.check_volume", side_effect=mock_functions.checkVolume)
    def test_run_volume_checker(self, mockCheckVolume):
        args = ["volume", "check", "-volume_id", "1"]
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockCheckVolume.call_count == 1

    @patch( "fdscli.services.volume_service.VolumeService.check_volume", side_effect=mock_functions.checkVolume)
    def test_run_volume_fixer(self, mockCheckVolume):
        args = ["volume", "check", "-volume_id", "1", "-fix"]
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockCheckVolume.call_count == 1


    @patch( "fdscli.services.local_domain_service.LocalDomainService.find_domain_by_id", side_effect=mock_functions.findDomainById)
    @patch( "fdscli.services.local_domain_service.LocalDomainService.check_tokens", side_effect=mock_functions.checkTokens)
    def test_run_tokens_checker(self, mockList, mockCheckTokens):
        args = ["local_domain", "check", "-domain_id", "1"]
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockCheckTokens.call_count == 1

    @patch( "fdscli.services.local_domain_service.LocalDomainService.find_domain_by_id", side_effect=mock_functions.findDomainById)
    @patch( "fdscli.services.local_domain_service.LocalDomainService.fix_tokens", side_effect=mock_functions.fixTokens)
    def test_run_tokens_fixer(self, mockList, mockFixTokens):
        args = ["local_domain", "fix", "-domain_id", "1"]
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockFixTokens.call_count == 1

