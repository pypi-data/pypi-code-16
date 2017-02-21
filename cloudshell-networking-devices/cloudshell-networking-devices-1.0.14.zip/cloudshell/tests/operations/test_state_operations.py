#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from mock import patch, MagicMock as Mock

from cloudshell.networking.devices.runners import StateOperations
from cloudshell.shell.core.context import ResourceCommandContext, ReservationContextDetails, ResourceContextDetails


class TestStateOperations(unittest.TestCase):
    def setUp(self):
        super(TestStateOperations, self).setUp()
        with patch("cloudshell.networking.runners.state_operations.StateOperations"):
            StateOperations.__abstractmethods__ = frozenset()
            api = Mock()
            cli = Mock()
            logger = Mock()
            context = ResourceCommandContext()
            context.resource = ResourceContextDetails()
            context.resource.name = "resource_name"
            context.reservation = ReservationContextDetails()
            context.reservation.reservation_id = "reservation_ID"
            context.resource.attributes = dict()
            context.resource.attributes["CLI Connection Type"] = "Telnet"
            context.resource.attributes["Sessions Concurrency Limit"] = "1"
            self.tested_instance = StateOperations(api=api, cli=cli, logger=logger, context=context)
            self.tested_instance._session_type = Mock()

    def tearDown(self):
        super(TestStateOperations, self).tearDown()
        del self.tested_instance

    def test__wait_device_down_no_session_type(self):
        with self.assertRaises(Exception):
            self.tested_instance._session_type = None
            self.tested_instance._wait_device_down()

    def test__wait_device_down_cannot_get_session(self):
        self.tested_instance._cli.get_session.return_value = Exception
        self.assertTrue(self.tested_instance._wait_device_down())

    @patch("cloudshell.networking.runners.state_operations.time.sleep")
    def test__wait_device_down(self, mock_time_sleep):
        session = Mock()
        session.send_command = Mock(side_effect=[Mock(), Mock()])
        session_context = Mock(__enter__=Mock(return_value=session))
        self.tested_instance._cli.get_session.return_value = session_context
        self.assertTrue(self.tested_instance._wait_device_down())
        self.assertEqual(session.send_command.call_count, 3)

    @patch("cloudshell.networking.runners.state_operations.time.sleep")
    def test__wait_device_down_session_not_closed(self, mock_time_sleep):
        session_context = Mock(__enter__=Mock(return_value=Mock()))
        self.tested_instance._cli.get_session.return_value = session_context
        self.assertFalse(self.tested_instance._wait_device_down(timeout=0))

    def test__wait_device_up_no_session_type(self):
        with self.assertRaises(Exception):
            self.tested_instance._session_type = None
            self.tested_instance._wait_device_up()

    def test__wait_device_up_cannot_get_session(self):
        self.tested_instance._cli.get_session.return_value = Exception
        self.assertFalse(self.tested_instance._wait_device_up(timeout=0))

    @patch("cloudshell.networking.runners.state_operations.time.sleep")
    def test__wait_device_up(self, mock_time_sleep):
        session = Mock()
        session.send_command = Mock(side_effect=[Exception, Exception, Mock()])
        session_context = Mock(__enter__=Mock(return_value=session))
        self.tested_instance._cli.get_session.return_value = session_context
        self.assertTrue(self.tested_instance._wait_device_up())
        self.assertEqual(session.send_command.call_count, 3)
