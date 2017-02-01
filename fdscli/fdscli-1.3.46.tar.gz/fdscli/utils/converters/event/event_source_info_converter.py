# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
import json

from fdscli.model.event.event_source_info import EventSourceInfo


class EventSourceInfoConverter(object):
    '''Helper class for marshalling between EventSourceInfo and JSON formatted string.

    The term 'to marshal' means to convert some data from internal to external form
    (in an RPC buffer for instance). The term 'unmarshalling' refers to the reverse
    process. We presume that the server will use reflection to create a Java object
    given the JSON formatted string.
    '''

    @staticmethod
    def to_json(event_source):
        """
        :param event_source: ``model.event.EventSourceInfo`` object to convert to JSON dict
        :return: a dict representing the ``model.event.EventSourceInfo`` object that follows the JSON convention
        """
        json_d = {}

        if event_source is not None:

            json_d = {
                "sourceId": event_source.source_id,
                "nodeId": event_source.node_id,
                "nodeAddress": event_source.node_address,
                "pid": event_source.pid,
                "processName": event_source.process_name,
                "serviceId": event_source.service_id,
                "serviceType": event_source.service_type,
                "serviceVersion": event_source.service_version,
                "domainId": event_source.domain_id,
                "domainName": event_source.domain_name,
                "attributes": event_source.attributes
            }

        return json_d

    @staticmethod
    def to_json_string(event):
        '''Converts ``model.event.EventSourceInfo`` object into a JSON formatted string.

        We presume that the recipient (a server) uses a package like Gson and passes the type
        literal when deserializing the JSON formatted string.

        Parameters
        ----------
        :type event: ``model.event.EventSourceInfo`` object

        Returns
        -------
        :type string
        '''

        d = EventSourceInfoConverter.to_json(event)

        result = json.dumps(d)
        return result

    @staticmethod
    def build_from_json(j_str):
        '''Produce a ``model.event.EventSourceInfo`` object from deserialized server response

        Parameters
        ----------
        :type j_str: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type ``model.event.EventSourceInfo``
        '''
        source_info = EventSourceInfo()

        # If given argument not a dict, decode to a dict
        if not isinstance(j_str, dict):
            j_str = json.loads(j_str)

        if "sourceId" in j_str:
            source_info.source_id = j_str.pop("sourceId", source_info.source_id)

        if "nodeId" in j_str:
            source_info.node_id = j_str.pop("nodeId", source_info.node_id)

        if "nodeAddress" in j_str:
            source_info.node_address = j_str.pop("nodeAddress", source_info.node_address)

        if "pid" in j_str:
            source_info.pid = j_str.pop("pid", source_info.pid)

        if "processName" in j_str:
            source_info.process_name = j_str.pop("processName", source_info.process_name)

        if "serviceId" in j_str:
            source_info.service_id = j_str.pop("serviceId", source_info.service_id)

        if "serviceType" in j_str:
            source_info.service_type = j_str.pop("serviceType", source_info.service_type)

        if "serviceVersion" in j_str:
            source_info.service_version = j_str.pop("serviceVersion", source_info.service_version)

        if "domainId" in j_str:
            source_info.domain_id = j_str.pop("domainId", source_info.domain_id)

        if "domainName" in j_str:
            source_info.domain_name = j_str.pop("domainName", source_info.domain_name)

        if "attributes" in j_str:
            source_info.attributes = j_str.pop("attributes", source_info.attributes)

        return source_info
