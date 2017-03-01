# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json

from fdscli.model.event.event import Event, EventContent
from fdscli.utils.converters.event.event_descriptor_converter import EventDescriptorConverter
from fdscli.utils.converters.event.event_source_info_converter import EventSourceInfoConverter



class EventConverter(object):
    '''Helper class for marshalling between Event and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(event):
        """
        :param event: ``model.event.Event`` object to convert to JSON dict
        :return: a dict representing the ``model.event.Event`` object that follows the JSON convention
        """

        json_d = dict()

        if event.uuid == -1:
            json_d["type"] = event.e_type
            json_d["event"] = EventContentConverter.to_json(event.event_content)
            json_d["locale"] = event.locale
            json_d["eventMessage"] = event.event_message
        else:
            json_d["uuid"] = event.uuid
            json_d["messageKey"] = event.message_key
            json_d["defaultMessage"] = event.default_message
            json_d["initialTimestamp"] = event.creation_time
            json_d["severity"] = event.severity
            json_d["categories"] = event.categories
            json_d["messageArgs"] = event.message_args

        return json_d

    @staticmethod
    def to_json_string(event):
        '''Converts ``model.event.Event`` object into a JSON formatted string.

        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        :type event: ``model.event.Event`` object

        Returns
        -------
        :type string
        '''

        d = EventConverter.to_json(event)

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
        event = Event()

        # If given argument not a dict, decode to a dict
        if not isinstance(j_str, dict):
            j_str = json.loads(j_str)

        if "messageArgs" in j_str:
            event.message_args = j_str.pop("messageArgs", event.message_args)

        if "messageKey" in j_str:
            event.message_key = j_str.pop("messageKey", event.message_key)

        if "uuid" in j_str:
            event.uuid = j_str.pop("uuid", event.uuid)

        if "defaultMessage" in j_str:
            event.default_message = j_str.pop("defaultMessage", event.default_message)

        if 'initialTimestamp' in j_str:
            event.creation_time = j_str.pop("initialTimestamp", event.creation_time)

        if 'severity' in j_str:
            event.severity = j_str.pop("severity", event.severity)

        # v08 model only supported a single category, but event service model is 
        # a list
        if 'categories' in j_str:
            event.categories = j_str.pop("categories", event.categories)
        elif 'category' in j_str:
            #event.categories = []
            #event.categories.append(j_str.pop("category", event.categories))
            event.categories = j_str.pop("category", event.categories)

        if "type" in j_str:
            event.e_type = j_str.pop("type", event.e_type)

        if "event" in j_str:
            event.event_content = EventContentConverter\
                .build_from_json(j_str.pop("event", event.event_content))

        if "locale" in j_str:
            event.locale = j_str.pop("locale", event.locale)

        if "eventMessage" in j_str:
            event.event_message = j_str.pop("eventMessage", event.event_message)

        return event


class EventContentConverter(object):
    '''Helper class for marshalling between EventContent and JSON formatted string.

        The term 'to marshal' means to convert some data from internal to external form
        (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
        process. We presume that the server will use reflection to create a Java object
        given the JSON formatted string.
        '''

    @staticmethod
    def to_json(event_content):
        """
        :param event_content: ``model.event.EventContent`` object to convert to JSON dict
        :return: a dict representing the ``model.event.EventContent`` object that follows the JSON convention
        """

        json_d = dict()

        json_d["type"] = event_content.e_type
        json_d["timestamp"] = event_content.timestamp
        json_d["descriptor"] = EventDescriptorConverter.to_json(event_content.descriptor)
        json_d["sourceInfo"] = EventSourceInfoConverter.to_json(event_content.source_info)
        json_d["attributes"] = event_content.attributes

        return json_d

    @staticmethod
    def to_json_string(event_content):
        '''Converts ``model.event.EventContent`` object into a JSON formatted string.

        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        :type event_content: ``model.event.EventContent`` object

        Returns
        -------
        :returns string
        '''

        d = EventContentConverter.to_json(event_content)

        result = json.dumps(d)
        return result

    @staticmethod
    def build_from_json(j_str):
        '''Produce a ``model.event.EventContent`` object from deserialized server response

        Parameters
        ----------
        :type j_str: dict or json-encoded string representing a JSON object

        Returns
        -------
        :returns ``model.event.EventContent``
        '''
        event_content = EventContent()

        # If given argument not a dict, decode to a dict
        if not isinstance(j_str, dict):
            j_str = json.loads(j_str)

        if "type" in j_str:
            event_content.e_type = j_str.pop("type", event_content.e_type)

        if "timestamp" in j_str:
            event_content.timestamp = j_str.pop("timestamp", event_content.timestamp)

        if "descriptor" in j_str:
            event_content.descriptor = EventDescriptorConverter\
                .build_from_json(j_str.pop("descriptor", event_content.descriptor))

        if "sourceInfo" in j_str:
            event_content.source_info = EventSourceInfoConverter\
                .build_from_json(j_str.pop("sourceInfo", event_content.source_info))

        if "attributes" in j_str:
            event_content.attributes = j_str.pop("attributes", event_content.attributes)

        return event_content
