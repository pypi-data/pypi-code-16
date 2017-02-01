#
# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
from test.base_cli_test import BaseCliTest
from mock import patch
import json
import mock_functions
import requests
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.rest_helper import RESTHelper

def mock_post_accepted( url, data, headers, verify, timeout ):
    '''
    Supplies a requests.Response object with code accepted.
    '''
    response = requests.Response()
    response.status_code = 202
    response.encoding = "utf-8"
    return response

def mock_post_no_content( url, data, headers, verify, timeout ):
    '''
    Supplies a requests.Response object with code no_content.
    '''
    response = requests.Response()
    response.status_code = 204
    response.encoding = "utf-8"
    return response

def mock_header(session):
    '''
    Supplies a fake header
    '''
    return { "FDS-Auth" : "fake_token" }

class RequestHelperTest( BaseCliTest ):
    '''
    Test case for RESTHelper. IS-A unittest.TestCase.
    '''

    @patch("requests.post", side_effect=mock_post_accepted)
    @patch("fdscli.services.rest_helper.RESTHelper.buildHeader", side_effect=mock_header)
    def test_post_accepted(self, mockServiceHeader, mockRequestsPost):
        '''
        Test response 202 accepted.

        Parameters
        ----------
        mockServiceHeader (unittest.mock.MagicMock)
        mockRequestsPost (unittest.mock.MagicMock)
        '''
        session = FdsAuth()
        url = "http://localhost:7777/fds/config/v09/volumes/42/exports/s3?incremental=true"

        helper = RESTHelper()
        response = helper.post(session,  url)

        d = json.loads(response)
        assert d["code"] == 202
        assert d["description"] == "accepted"

    @patch("requests.post", side_effect=mock_post_no_content)
    @patch("fdscli.services.rest_helper.RESTHelper.buildHeader", side_effect=mock_header)
    def test_post_no_content(self, mockServiceHeader, mockRequestsPost):
        '''
        Test response 204 no_content.

        Parameters
        ----------
        mockServiceHeader (unittest.mock.MagicMock)
        mockRequestsPost (unittest.mock.MagicMock)
        '''
        session = FdsAuth()
        url = "http://localhost:7777/fds/config/v09/volumes/42/exports/s3?incremental=true"

        helper = RESTHelper()
        response = helper.post(session,  url)

        d = json.loads(response)
        assert d["code"] == 204

