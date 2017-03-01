# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import collections
import json
from fdscli.services.abstract_service import AbstractService
from fdscli.model.fds_error import FdsError
from fdscli.model.volume.subscription import Subscription
from fdscli.utils.converters.volume.subscription_converter import SubscriptionConverter

class SubscriptionClient(AbstractService):
    '''
    Formation Subscription
    Formation Subscription is a web service that enables a volume to subscribe to one or
    more SafeGuard policies. SafeGuard policies enable management of data migration tasks.
    Each SafeGuard policy can reference a durable storage endpoint and specify a recurrence
    rule for data migration.

    To provide end-user credentials, first use the CredentialsClient and make a call to
    create. That call will provide a unique identifier for the persisted credentials. Each
    named credential supplies a URL for the data migration destination.

    Client
    This low-level API provides one-to-one mappings to the underlying HTTP API operations.
    '''

    def __init__(self, session):
        '''
        :type session: ``services.FdsAuth``
        :param session: Data about the active session
        '''
        AbstractService.__init__(self, session)

    def create_subscription(self, subscription):
        '''Create a subscription

        Parameters
        ----------
        :type subscription: ``model.volume.Subscription``
        :param subscription: Subscription object

        Returns
        -------
        :type ``model.FdsError`` or ``model.volume.Subscription``
        '''
        j_str = SubscriptionConverter.to_json(subscription)

        # Adds additional members
        d = json.loads(j_str)
        d["primaryDomainId"] = 0

        url="{}{}".format(self.get_url_preamble(), "/subscriptions")
        data = json.dumps(d)

        response = self.rest_helper.post(self.session, url, data)

        if isinstance(response, FdsError):
            return response

        # Validate named credential digest
        if "namedCredentialDigest" in response:
            credential_digest = response.pop("namedCredentialDigest")
            if credential_digest != subscription.named_credential.digest:
                return FdsError("Error: named credential Id does not match subscription.")

        deserialized = SubscriptionConverter.build_from_json(response)
        if deserialized is None:
            return
        if isinstance(deserialized, Subscription):
            # Put the named credential back after checking digest match
            deserialized.named_credential = subscription.named_credential
        return deserialized

    def get_subscription_by_name(self, name, volume_id):
        '''
        Returns
        -------
        :type ``model.FdsError`` or ``model.volume.Subscription`` or None
        '''
        if name is None or len(name) == 0:
            return None
        response = self.list_subscriptions(volume_id)
        if isinstance(response, FdsError):
            return response
        if not isinstance(response, collections.Iterable):
            return None
        for subscription in response:
            if not isinstance(subscription, Subscription):
                continue
            if subscription.name == name:
                return subscription
        return None

    def list_subscriptions(self, volume_id):
        '''Request list of subscriptions, optionally filtered for a given volume.

        Parameters
        ----------
        :type volume_id: int or None
        :param volume_id: Unique identifier for a volume or None for all subscriptions

        Returns
        -------
        :type ``model.FdsError`` or list(``Subscription``)
        '''
        if volume_id is not None:
            url = "{}{}{}{}".format(self.get_url_preamble(), "/volumes/", volume_id, "/subscriptions")
        else:
            url = "{}{}".format(self.get_url_preamble(), "/subscriptions")

        response = self.rest_helper.get(self.session, url)

        if isinstance(response, FdsError):
            return response

        subscriptions = []

        for j_subscription in response:
            # Pull out the named credential digest
            credential_digest = None
            if "namedCredentialDigest" in j_subscription:
                credential_digest = j_subscription.pop("namedCredentialDigest")
            subscription = SubscriptionConverter.build_from_json(j_subscription)
            if credential_digest is not None:
                subscription.named_credential.digest = credential_digest
            subscriptions.append(subscription)

        return subscriptions

    def delete_all_subscriptions(self, volume_id):
        '''Delete all subscriptions for a given volume.

        Parameters
        ----------
        :type volume_id: int
        :param volume_id: Unique identifier for a volume

        Returns
        -------
        :type ``model.FdsError`` or bool
        '''
        url = "{}{}{}".format(self.get_url_preamble(), "/subscriptions/", volume_id)
        response = self.rest_helper.get(self.session, url)

        if isinstance(response, FdsError):
            return response

        for j_subscription in response:
            digest = j_subscription.pop("digest")
            response2 = self.delete_subscription(digest)
            if isinstance(response, FdsError):
                return response

        return True

    def delete_subscription(self, digest):
        '''Delete a subscription

        Parameters
        ----------
        :type digest: string

        Returns
        -------
        :type ``model.FdsError`` or bool
        '''
        if digest is None:
            return False
        url="{}{}{}".format(self.get_url_preamble(), "/subscriptions/", digest)
        response = self.rest_helper.delete(self.session, url)

        if isinstance(response, FdsError):
            return response

        # TODO: What if not found or other failure to delete?
        return True
