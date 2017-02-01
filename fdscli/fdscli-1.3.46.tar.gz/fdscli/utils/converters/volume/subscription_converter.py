# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.volume.subscription import Subscription
from fdscli.utils.converters.volume.recurrence_rule_converter import RecurrenceRuleConverter

class SubscriptionConverter(object):
    '''Helper class for marshalling between Subscription and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(subscription):
        '''Converts ``model.volume.Subscription`` object into a JSON formatted string.

        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        :type subscription: ``model.volume.Subscription`` object

        Returns
        -------
        :type string
        '''
        d = dict()

        d["digest"] = subscription.digest
        d["name"] = subscription.name
        d["primaryVolumeId"] = subscription.volume_id
        d["createTime"] = subscription.creation_time
        if subscription.remote_volume is not None:
            d["remoteVolumeName"] = subscription.remote_volume

        if subscription.recurrence_rule is not None:
            j_recurrenceRule = RecurrenceRuleConverter.to_json(subscription.recurrence_rule)
            d["recurrenceRule"] = json.loads(j_recurrenceRule)

        if subscription.named_credential is not None:
            d["namedCredentialDigest"] = subscription.named_credential.digest

        result = json.dumps(d)
        return result;

    @staticmethod
    def build_from_json(j_str):
        '''Produce a ``model.volume.Subscription`` object from deserialized server response

        Parameters
        ----------
        :type j_str: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type ``model.volume.Subscription``
        '''
        subscription = Subscription()

        # If given argument not a dict, decode to a dict
        if not isinstance(j_str, dict):
            j_str = json.loads(j_str)
        subscription.digest = j_str.pop("digest", subscription.digest)
        subscription.name = j_str.pop("name", subscription.name)
        subscription.volume_id = j_str.pop("primaryVolumeId", subscription.volume_id)
        subscription.creation_time = j_str.pop("createTime", subscription.creation_time)

        if "remoteVolumeName" in j_str:
            subscription.remote_volume = j_str.pop("remoteVolumeName", subscription.remote_volume)

        if "recurrenceRule" in j_str:
            j_recur =  j_str.pop("recurrenceRule", subscription.recurrence_rule)
            if isinstance(j_recur, dict):
                subscription.recurrence_rule = RecurrenceRuleConverter.build_rule_from_json(j_recur)

        if "namedCredentialDigest" in j_str:
            subscription.named_credential = NamedCredential(digest=j_str.pop("namedCredentialDigest"))

        return subscription
