# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#

from test.base_cli_test import BaseCliTest
from mock import patch
import mock_functions
from fdscli.model.fds_error import FdsError
from fdscli.model.volume.subscription import Subscription
from fdscli.services.fds_auth import FdsAuth
from fdscli.services.subscription.subscription_client import SubscriptionClient

def mock_create_subscription(subscription):
    subscription.digest = 'abcdef01'
    return subscription

def mock_list_subscriptions(volume_id):
    '''Request list of subscriptions for a given volume.

    Parameters
    ----------
    :type volume_id: int
    :param volume_id: Unique identifier for a volume

    Returns
    -------
    :type ``model.FdsError`` or list(``Subscription``)
    '''
    subscriptions = []
    subscription = Subscription(digest="abcdef01",
        name="name1",
        volume_id=volume_id)
    subscriptions.append(subscription)
    subscription = Subscription(digest="abcdef02",
        name="name2",
        volume_id=volume_id)
    subscriptions.append(subscription)
    return subscriptions

def mock_get_request(session, url):
    print url
    response = FdsError()
    return response

def mock_get_url_preamble():
    return "http://localhost:7777/fds/config/v09"

class VolumeSafeGuardTest( BaseCliTest ):
    '''Tests plugin and service client functionality for 'volume safeguard' command.

    IS-A unittest.TestCase.
    '''

    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credential_by_key", side_effect=mock_functions.getNamedCredentialByKey)
    @patch("fdscli.services.volume_service.VolumeService.get_safeguard_presets", side_effect=mock_functions.listSafeGuardPresets)
    @patch("fdscli.services.subscription.subscription_client.SubscriptionClient.create_subscription", side_effect=mock_create_subscription)
    @patch("fdscli.services.subscription.subscription_client.SubscriptionClient.list_subscriptions", side_effect=mock_list_subscriptions)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credentials", side_effect=mock_functions.empty)
    def test_add_cdr_subscription(self, mock_credentials, mock_subscriptions, mock_subscription, mock_presets, mock_credential):
        '''Tests the volume plugin for 'volume safeguard add'.

        Parameters
        ----------
        :type mock_credentials: ``unittest.mock.MagicMock``
        :type mock_subscriptions: ``unittest.mock.MagicMock``
        :type mock_subscription: ``unittest.mock.MagicMock``
        :type mock_presets: ``unittest.mock.MagicMock``
        :type mock_credential: ``unittest.mock.MagicMock``
        '''
        # Adds a CDR-Snap subscription
        volume_id = 11
        subscription_name = 'name1'
        credential_name = 'fakef1'
        args = ["volume", "safeguard", "add", subscription_name, credential_name, str(volume_id)]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mock_subscription.call_count == 1
        assert mock_presets.call_count == 1
        assert mock_credentials.call_count == 1
        assert mock_credential.call_count == 1

        subscription = mock_subscription.call_args[0][0]
        assert subscription.digest == 'abcdef01'
        assert subscription.name == subscription_name
        assert subscription.named_credential.name == 'fakef1'
        assert subscription.remote_volume == 'replica-11-name1'
        assert subscription.volume_id == str(volume_id)

        print("test_add_cdr_subscription passed.\n\n")

    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credential_by_key", side_effect=mock_functions.getNamedCredentialByKey)
    @patch("fdscli.services.volume_service.VolumeService.get_safeguard_presets", side_effect=mock_functions.listSafeGuardPresets)
    @patch("fdscli.services.subscription.subscription_client.SubscriptionClient.create_subscription", side_effect=mock_create_subscription)
    @patch("fdscli.services.subscription.subscription_client.SubscriptionClient.list_subscriptions", side_effect=mock_list_subscriptions)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credentials", side_effect=mock_functions.empty)
    def test_add_cdm_subscription(self, mock_credentials, mock_subscriptions, mock_subscription, mock_presets, mock_credential):
        '''Tests the volume plugin for 'volume safeguard add'.

        Parameters
        ----------
        :type mock_credentials: ``unittest.mock.MagicMock``
        :type mock_subscriptions: ``unittest.mock.MagicMock``
        :type mock_subscription: ``unittest.mock.MagicMock``
        :type mock_presets: ``unittest.mock.MagicMock``
        :type mock_credential: ``unittest.mock.MagicMock``
        '''
        # Adds a CDM-Snap subscription
        volume_id = 11
        subscription_name = 'name2'
        credential_name = 'fakes3'
        args = ["volume", "safeguard", "add", subscription_name, credential_name, str(volume_id)]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mock_subscription.call_count == 1
        assert mock_presets.call_count == 1
        assert mock_credentials.call_count == 1
        assert mock_credential.call_count == 1

        subscription = mock_subscription.call_args[0][0]
        assert subscription.digest == 'abcdef01'
        assert subscription.name == subscription_name
        assert subscription.named_credential.name == 'fakes3'
        assert subscription.named_credential.bucketname == 'tinpail'
        assert subscription.volume_id == str(volume_id)

        print("test_add_cdm_subscription passed.\n\n")

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.subscription.named_credential_client.NamedCredentialClient.get_named_credentials", side_effect=mock_functions.empty)
    @patch("fdscli.services.subscription.subscription_client.SubscriptionClient.list_subscriptions", side_effect=mock_list_subscriptions)
    def test_list_by_volume(self, mockListSubscriptions, mock_credentials, mockTabular, mockPretty):
        '''Tests the volume plugin for 'volume safeguard list'.

        The subscription service calls are replaced by mock functions.

        Parameters
        ----------
        :type mockListSubscriptions: ``unittest.mock.MagicMock``
        :type mock_credentials: ``unittest.mock.MagicMock``
        :type mockTabular: ``unittest.mock.MagicMock``
        :type mockPretty: ``unittest.mock.MagicMock``
        '''
        args = ["volume", "safeguard", "list", "-volume_id=11"]

        self.callMessageFormatter(args)
        self.cli.run(args)
        assert mockListSubscriptions.call_count == 1

        volume_id = mockListSubscriptions.call_args[0][0]
        assert volume_id == 11

        print("test_list_by_volume passed.\n\n")

    @patch("fdscli.plugins.volume_plugin.VolumePlugin.pretty_print_volume", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.abstract_service.AbstractService.get_url_preamble", side_effect=mock_get_url_preamble)
    @patch("fdscli.services.rest_helper.RESTHelper.get", side_effect=mock_get_request)
    def test_client_list_subscriptions(self, mockServiceGet, mockUrlPreamble, mockTabular, mockPretty):
        '''Directly tests the real SubscriptionClient.list_subscriptions API.

        Parameters
        ----------
        :type mockServiceGet: ``unittest.mock.MagicMock``
        :param mockServiceGet: Replace REST helper get() with mock empty

        :type mockUrlPreamble: ``unittest.mock.MagicMock``
        :param mockUrlPreamble: Returns the string to prepend for GET Url

        :type mockTabular: ``unittest.mock.MagicMock``
        :type mockPretty: ``unittest.mock.MagicMock``
        '''
        volume_id = 11

        session = FdsAuth()
        client = SubscriptionClient(session)
        client.list_subscriptions(volume_id)

        # The client list_subscription is a url producer
        assert mockServiceGet.call_count == 1
        url = mockServiceGet.call_args[0][1]
        assert url == "http://localhost:7777/fds/config/v09/volumes/11/subscriptions"

        print("test_client_list_subscriptions passed.\n\n")

