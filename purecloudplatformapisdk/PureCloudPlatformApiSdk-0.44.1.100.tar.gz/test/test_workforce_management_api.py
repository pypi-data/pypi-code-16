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
from swagger_client.apis.workforce_management_api import WorkforceManagementApi


class TestWorkforceManagementApi(unittest.TestCase):
    """ WorkforceManagementApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.workforce_management_api.WorkforceManagementApi()

    def tearDown(self):
        pass

    def test_get_adherence(self):
        """
        Test case for get_adherence

        Get a list of UserScheduleAdherence records for the requested users
        """
        pass

    def test_get_managementunits(self):
        """
        Test case for get_managementunits

        Get management units
        """
        pass

    def test_get_managementunits_mu_id_activitycodes(self):
        """
        Test case for get_managementunits_mu_id_activitycodes

        Get activity codes corresponding to a management unit
        """
        pass

    def test_get_managementunits_mu_id_users(self):
        """
        Test case for get_managementunits_mu_id_users

        Get agents in the management unit
        """
        pass

    def test_get_managementunits_mu_id_users_user_id_timeoffrequests(self):
        """
        Test case for get_managementunits_mu_id_users_user_id_timeoffrequests

        Get a list of time off requests for any user
        """
        pass

    def test_get_managementunits_mu_id_users_user_id_timeoffrequests_timeoffrequest_id(self):
        """
        Test case for get_managementunits_mu_id_users_user_id_timeoffrequests_timeoffrequest_id

        Get a time off request by id
        """
        pass

    def test_get_timeoffrequests(self):
        """
        Test case for get_timeoffrequests

        Get a list of time off requests for the current user
        """
        pass

    def test_get_timeoffrequests_timeoffrequest_id(self):
        """
        Test case for get_timeoffrequests_timeoffrequest_id

        Get a time off request for the current user by id
        """
        pass

    def test_patch_timeoffrequests_timeoffrequest_id(self):
        """
        Test case for patch_timeoffrequests_timeoffrequest_id

        Mark a time off request for the current user as read or unread
        """
        pass

    def test_post_managementunits_mu_id_schedules_search(self):
        """
        Test case for post_managementunits_mu_id_schedules_search

        Get user schedules within the given time range
        """
        pass

    def test_post_schedules(self):
        """
        Test case for post_schedules

        Get a schedule for the current user
        """
        pass


if __name__ == '__main__':
    unittest.main()