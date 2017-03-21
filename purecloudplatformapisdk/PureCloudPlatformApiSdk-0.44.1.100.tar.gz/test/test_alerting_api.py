# coding: utf-8

"""
Copyright 2016 SmartBear Software

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   ref: https://github.com/swagger-api/swagger-codegen
"""

from __future__ import absolute_import

import os
import sys
import unittest

import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis.alerting_api import AlertingApi


class TestAlertingApi(unittest.TestCase):
    """ AlertingApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.alerting_api.AlertingApi()

    def tearDown(self):
        pass

    def test_delete_heartbeat_alerts_alert_id(self):
        """
        Test case for delete_heartbeat_alerts_alert_id

        Delete a heart beat alert
        """
        pass

    def test_delete_heartbeat_rules_rule_id(self):
        """
        Test case for delete_heartbeat_rules_rule_id

        Delete a heart beat rule.
        """
        pass

    def test_delete_interactionstats_alerts_alert_id(self):
        """
        Test case for delete_interactionstats_alerts_alert_id

        Delete an interaction stats alert
        """
        pass

    def test_delete_interactionstats_rules_rule_id(self):
        """
        Test case for delete_interactionstats_rules_rule_id

        Delete an interaction stats rule.
        """
        pass

    def test_delete_routingstatus_alerts_alert_id(self):
        """
        Test case for delete_routingstatus_alerts_alert_id

        Delete a routing status alert
        """
        pass

    def test_delete_routingstatus_rules_rule_id(self):
        """
        Test case for delete_routingstatus_rules_rule_id

        Delete a routing status rule.
        """
        pass

    def test_delete_userpresence_alerts_alert_id(self):
        """
        Test case for delete_userpresence_alerts_alert_id

        Delete a user presence alert
        """
        pass

    def test_delete_userpresence_rules_rule_id(self):
        """
        Test case for delete_userpresence_rules_rule_id

        Delete a user presence rule.
        """
        pass

    def test_get_heartbeat_alerts(self):
        """
        Test case for get_heartbeat_alerts

        Get heart beat alert list.
        """
        pass

    def test_get_heartbeat_alerts_alert_id(self):
        """
        Test case for get_heartbeat_alerts_alert_id

        Get a heart beat alert
        """
        pass

    def test_get_heartbeat_rules(self):
        """
        Test case for get_heartbeat_rules

        Get a heart beat rule list.
        """
        pass

    def test_get_heartbeat_rules_rule_id(self):
        """
        Test case for get_heartbeat_rules_rule_id

        Get a heart beat rule.
        """
        pass

    def test_get_interactionstats_alerts(self):
        """
        Test case for get_interactionstats_alerts

        Get interaction stats alert list.
        """
        pass

    def test_get_interactionstats_alerts_alert_id(self):
        """
        Test case for get_interactionstats_alerts_alert_id

        Get an interaction stats alert
        """
        pass

    def test_get_interactionstats_alerts_unread(self):
        """
        Test case for get_interactionstats_alerts_unread

        Gets user unread count of interaction stats alerts.
        """
        pass

    def test_get_interactionstats_rules(self):
        """
        Test case for get_interactionstats_rules

        Get an interaction stats rule list.
        """
        pass

    def test_get_interactionstats_rules_rule_id(self):
        """
        Test case for get_interactionstats_rules_rule_id

        Get an interaction stats rule.
        """
        pass

    def test_get_routingstatus_alerts(self):
        """
        Test case for get_routingstatus_alerts

        Get routing status alert list.
        """
        pass

    def test_get_routingstatus_alerts_alert_id(self):
        """
        Test case for get_routingstatus_alerts_alert_id

        Get a routing status alert
        """
        pass

    def test_get_routingstatus_rules(self):
        """
        Test case for get_routingstatus_rules

        Get a routing status rule list.
        """
        pass

    def test_get_routingstatus_rules_rule_id(self):
        """
        Test case for get_routingstatus_rules_rule_id

        Get a routing status rule.
        """
        pass

    def test_get_userpresence_alerts(self):
        """
        Test case for get_userpresence_alerts

        Get user presence alert list.
        """
        pass

    def test_get_userpresence_alerts_alert_id(self):
        """
        Test case for get_userpresence_alerts_alert_id

        Get a user presence alert
        """
        pass

    def test_get_userpresence_rules(self):
        """
        Test case for get_userpresence_rules

        Get a user presence rule list.
        """
        pass

    def test_get_userpresence_rules_rule_id(self):
        """
        Test case for get_userpresence_rules_rule_id

        Get a user presence rule.
        """
        pass

    def test_post_heartbeat_rules(self):
        """
        Test case for post_heartbeat_rules

        Create a heart beat rule.
        """
        pass

    def test_post_interactionstats_rules(self):
        """
        Test case for post_interactionstats_rules

        Create an interaction stats rule.
        """
        pass

    def test_post_routingstatus_rules(self):
        """
        Test case for post_routingstatus_rules

        Create a routing status rule.
        """
        pass

    def test_post_userpresence_rules(self):
        """
        Test case for post_userpresence_rules

        Create a user presence rule.
        """
        pass

    def test_put_heartbeat_rules_rule_id(self):
        """
        Test case for put_heartbeat_rules_rule_id

        Update a heart beat rule
        """
        pass

    def test_put_interactionstats_alerts_alert_id(self):
        """
        Test case for put_interactionstats_alerts_alert_id

        Update an interaction stats alert read status
        """
        pass

    def test_put_interactionstats_rules_rule_id(self):
        """
        Test case for put_interactionstats_rules_rule_id

        Update an interaction stats rule
        """
        pass

    def test_put_routingstatus_rules_rule_id(self):
        """
        Test case for put_routingstatus_rules_rule_id

        Update a routing status rule
        """
        pass

    def test_put_userpresence_rules_rule_id(self):
        """
        Test case for put_userpresence_rules_rule_id

        Update a user presence rule
        """
        pass


if __name__ == '__main__':
    unittest.main()