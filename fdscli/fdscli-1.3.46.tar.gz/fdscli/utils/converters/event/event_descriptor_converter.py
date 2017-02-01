# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json

from fdscli.model.event.event_descriptor import EventDescriptor


# "descriptor" : {
#      "type" : "com.formationds.events.model.EventDescriptor",
#      "key" : "testservice.test_event",
#      "severity" : "CONFIG",
#      "categories" : [ "SERVICE", "USER" ],
#      "messageFormat" : "User $user$ configured the service $svc$",
#      "messageAttributeNames" : [ "user", "svc" ]
#    },

class EventDescriptorConverter(object):
    '''Helper class for marshalling between EventDescriptor and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(event_descriptor):
        """
        :param event_descriptor: ``model.event.EventDescriptor`` object to convert to JSON dict
        :return: a dict representing the ``model.event.EventDescriptor`` object that follows the JSON convention
        """

        json_d = dict()

        json_d["type"] = event_descriptor.e_type
        json_d["key"] = event_descriptor.key
        json_d["severity"] = event_descriptor.severity
        json_d["categories"] = event_descriptor.categories
        json_d["messageFormat"] = event_descriptor.message_format
        json_d["messageAttributeNames"] = event_descriptor.message_attribute_names

        return json_d

    @staticmethod
    def to_json_string(event_descriptor):
        """Converts ``model.event.EventDescriptor`` object into a JSON formatted string.

        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        :type event_descriptor: ``model.event.EventDescriptor`` object

        Returns
        -------
        :returns string
        """

        d = EventDescriptorConverter.to_json(event_descriptor)

        result = json.dumps(d)
        return result

    @staticmethod
    def build_from_json(j_str):
        '''Produce a ``model.event.Event`` object from deserialized server response

        Parameters
        ----------
        :type j_str: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type ``model.event.Event``
        '''
        event_descriptor = EventDescriptor()

        # If given argument not a dict, decode to a dict
        if not isinstance(j_str, dict):
            j_str = json.loads(j_str)

        if "type" in j_str:
            event_descriptor.e_type = j_str.pop("type", event_descriptor.e_type)

        if "key" in j_str:
            event_descriptor.key = j_str.pop("key", event_descriptor.key)

        if "severity" in j_str:
            event_descriptor.severity = j_str.pop("severity", event_descriptor.severity)

        if "categories" in j_str:
            event_descriptor.categories = j_str.pop("categories", event_descriptor.categories)

        if "messageFormat" in j_str:
            event_descriptor.message_format = j_str.pop("messageFormat", event_descriptor.message_format)

        if "messageAttributeNames" in j_str:
            event_descriptor.message_attribute_names = j_str.pop("messageAttributeNames",
                                                                 event_descriptor.message_attribute_names)

        return event_descriptor
