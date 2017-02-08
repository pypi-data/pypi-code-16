# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
import collections
import json
from fdscli.model.fds_error import FdsError
from fdscli.services.abstract_service import AbstractService
from fdscli.utils.converters.event.event_converter import EventConverter

class EventClient(AbstractService):
    '''
    Formation Event
    Formation Event is a web service that enables client code to subscribe to event
    notification.

    Client
    This low-level API provides one-to-one mappings to the underlying HTTP API operations.
    '''

    def __init__(self, session):
        '''
        :type session: ``services.FdsAuth``
        :param session: Data about the active session
        '''
        AbstractService.__init__(self, session)

    def build_default_query(self):
        '''
        Returns
        -------
        :type string
        '''
        order_bys = []

        o = dict()
        o["fieldName"] = 'initialTimestamp'
        o["ascending"] = False

        order_bys.append(o)

        d = dict()
        d["points"] = int(50)
        d["orderBys"] = order_bys

        result = json.dumps(d)
        return result;

    def list_events(self, query=None):
        '''Request list of events, optionally filtered using event query criteria.

        Parameters
        ----------
        :type query: ? or None
        :param query: a query for filtering or None for all events

        Returns
        -------
        :type ``model.FdsError`` or list(``Events``)
        '''
        url = "{}{}".format(self.get_url_preamble(), "/events")

        # TODO: enhance the CLI to permit a user-defined query
        if query is None:
            query = self.build_default_query()

        response = self.rest_helper.put(self.session, url, query)

        if isinstance(response, FdsError):
            return response

        events = []

        for j_event in response:
            event = EventConverter.build_from_json(j_event)
            events.append(event)

        return events
