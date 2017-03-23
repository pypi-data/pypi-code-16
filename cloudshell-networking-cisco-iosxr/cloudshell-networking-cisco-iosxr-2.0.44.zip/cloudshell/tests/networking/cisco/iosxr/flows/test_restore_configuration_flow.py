from unittest import TestCase

from mock import MagicMock
from cloudshell.networking.cisco.iosxr.flows.cisco_ios_xr_restore_flow import CiscoIOSXRRestoreFlow


class TestCiscorestoreConfigurationFlow(TestCase):
    def _get_handler(self, output):
        cli = MagicMock()
        self.session = MagicMock()
        self.config_session = MagicMock()
        self.session.send_command.return_value = output
        self.config_session.send_command.return_value = output
        cliservice = MagicMock()
        cliservice.__enter__.return_value = self.session
        cli.get_cli_service.return_value = cliservice
        self.session.enter_mode.return_value.__enter__.return_value = self.config_session
        logger = MagicMock()
        return CiscoIOSXRRestoreFlow(cli_handler=cli, logger=logger)

    def test_restore_configuration_fails_if_permissions_denied(self):
        restore_flow = self._get_handler("""load ftp://user:password@host_ip/Clouds$.233.30.222/Cloudsh
                                  ell/ASR10101 vrf managemen$0101 vrf management
                                  load ftp://user:password@host_ip/Cloud$
            % Couldn't open file ftp://admin:*@host;management/Cloudshell/ASR10101: Permission denied
            """)

        self.assertRaises(Exception, restore_flow.execute_flow, 'tftp://127.0.0.1', configuration_type='running',
                          restore_method="override", vrf_management_name='management')
        self.config_session.send_command.assert_called_once()

    def test_restore_configuration_fails_if_load_failed(self):
        restore_flow = self._get_handler("""load ftp://user:password@host_ip/C$.233.30.222/Cl                          +
        oudshell/ASR9001-1-running$001-1-running-
        060117-091831 vrf manageme$ vrf managemen
        tload ftp://user:password@host_ip/$
        Loading.
        0 bytes parsed in 120 sec (0)bytes/sec""")

        # restore_flow.execute_flow()
        self.assertRaises(Exception, restore_flow.execute_flow, 'tftp://127.0.0.1', configuration_type='running',
                          restore_method="override", vrf_management_name='management')
        self.config_session.send_command.assert_called_once()

    def test_restore_configuration(self):
        restore_flow = self._get_handler("""load ftp://user:password@host_ip/C$.333.33.222/Cl                          +
        oudshell/ASR9001-1-running$001-1-running-
        060117-091831 vrf manageme$ vrf managemen
        tload ftp://user:password@host_ip/$
        Loading.
        468 bytes parsed in 1 sec (467)bytes/sec""")

        restore_flow.execute_flow('tftp://127.0.0.1', 
                                  configuration_type='running', 
                                  restore_method="override", 
                                  vrf_management_name='management')
        self.config_session.send_command._call_matcher(2)
        self.config_session.send_command.assert_called()

    def test_restore_configuration_without_vrf(self):
        restore_flow = self._get_handler("""load ftp://user:password@host_ip/C$.333.33.222/Cl                          +
        oudshell/ASR9001-1-running$001-1-running-
        060117-091831 vrf manageme$ vrf managemen
        tload ftp://user:password@host_ip/$
        Loading.
        468 bytes parsed in 1 sec (467)bytes/sec""")

        restore_flow.execute_flow('tftp://127.0.0.1',
                                  configuration_type='running',
                                  restore_method="override")
        self.config_session.send_command._call_matcher(2)
        self.config_session.send_command.assert_called()

    def test_restore_configuration_append(self):
        restore_flow = self._get_handler("""C6504e-1-CE7#copy running-config tftp:
        Address or name of remote host []? 10.10.10.10
        Destination filename [c6504e-1-ce7-confg]? 6504e1
        !!
        23518 bytes copied in 0.904 secs (26015 bytes/sec)
        C6504e-1-CE7#""")

        restore_flow.execute_flow('tftp://127.0.0.1',
                                  configuration_type='startup',
                                  restore_method="append",
                                  vrf_management_name='management')
        self.session.send_command.assert_called_once()
