"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

import jsonpickle
from falkonryclient.helper.models.Subscription import Subscription

class Eventbuffer:
    """Eventbuffer schema class"""

    def __init__(self, **kwargs):
        self.raw = kwargs.get('eventbuffer') if 'eventbuffer' in kwargs else {}

        if 'subscriptionList' in self.raw:
            if isinstance(self.raw['subscriptionList'], list):
                subscriptions = []
                for subscription in self.raw['subscriptionList']:
                    subscriptions.append(Subscription(subscription=subscription))
                self.raw['subscriptionList'] = subscriptions

    def get_id(self):
        return self.raw['id'] if 'id' in self.raw else None

    def set_name(self, name):
        self.raw['name'] = name
        return self

    def get_name(self):
        return self.raw['name'] if 'name' in self.raw else None

    def set_source_id(self, source_id):
        self.raw['sourceId'] = source_id
        return self

    def get_source_id(self):
        return self.raw['sourceId'] if 'sourceId' in self.raw else None

    def get_account(self):
        return self.raw['tenant'] if 'tenant' in self.raw else None

    def get_create_time(self):
        return self.raw['createTime'] if 'createTime' in self.raw else None

    def get_created_by(self):
        return self.raw['createdBy'] if 'createdBy' in self.raw else None

    def get_update_time(self):
        return self.raw['updateTime'] if 'updateTime' in self.raw else None

    def get_updated_by(self):
        return self.raw['updatedBy'] if 'updatedBy' in self.raw else None

    def get_schema(self):
        return self.raw['schemaList'] if 'schemaList' in self.raw else []

    def set_subscriptions(self, subscriptions):
        subscription_list = self.raw['subscriptionList'] if 'subscriptionList' in self.raw else []
        for subscription in subscriptions:
            if isinstance(subscription, Subscription):
                subscription_list.append(subscription)

        self.raw['subscriptionList'] = subscription_list
        return self

    def get_subscriptions(self):
        return self.raw['subscriptionList'] if 'subscriptionList' in self.raw else []

    def set_signals_tag_field(self, signals_tag_field):
        self.raw['signalsTagField'] = signals_tag_field
        return self

    def get_signals_tag_field(self):
        return self.raw['signalsTagField'] if 'signalsTagField' in self.raw else None

    def set_signals_delimiter(self, signals_delimiter):
        self.raw['signalsDelimiter'] = signals_delimiter
        return self

    def get_signals_delimiter(self):
        return self.raw['signalsDelimiter'] if 'signalsDelimiter' in self.raw else None

    def set_signals_location(self, signals_location):
        self.raw['signalsLocation'] = signals_location
        return self

    def get_signals_location(self):
        return self.raw['signalsLocation'] if 'signalsLocation' in self.raw else None

    def set_value_column(self, value_column):
        self.raw['valueColumn'] = value_column
        return self

    def get_value_column(self):
        return self.raw['valueColumn'] if 'valueColumn' in self.raw else None    

    def set_entity_identifier(self, identifier):
        self.raw['entityIdentifier'] = identifier
        return self

    def get_entity_identifier(self):
        return self.raw['entityIdentifier'] if 'entityIdentifier' in self.raw else None

    def set_time_identifier(self, identifier):
        self.raw['timeIdentifier'] = identifier
        return self

    def get_time_identifier(self):
        return self.raw['timeIdentifier'] if 'timeIdentifier' in self.raw else None

    def set_time_format(self, time_format):
        self.raw['timeFormat'] = time_format
        return self

    def get_time_format(self):
        return self.raw['timeFormat'] if 'timeFormat' in self.raw else None

    def set_timezone(self, zone=None, offset=None):
        self.raw['interval'] = {
          'zone': zone,
          'offset': offset
        }
        return self

    def get_time_format(self):
        return self.raw['timezone'] if 'timezone' in self.raw else None

    def to_json(self):
        subscriptions = []
        for subscription in self.get_subscriptions():
            subscriptions.append(jsonpickle.unpickler.decode(subscription.to_json()))

        eventbuffer = self.raw
        eventbuffer['subscriptionList'] = subscriptions
        return jsonpickle.pickler.encode(eventbuffer)