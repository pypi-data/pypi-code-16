"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

import json


class Subscription:
    """Subscription schema class"""

    def __init__(self, **kwargs):
        self.raw = kwargs.get('subscription') if 'subscription' in kwargs else {}

    def get_key(self):
        return self.raw['key'] if 'key' in self.raw else None

    def set_type(self, subscription_type):
        self.raw['type'] = subscription_type
        return self

    def get_type(self):
        return self.raw['type'] if 'type' in self.raw else None

    def set_topic(self, topic):
        self.raw['topic'] = topic
        return self

    def get_topic(self):
        return self.raw['topic'] if 'topic' in self.raw else None

    def set_path(self, path):
        self.raw['path'] = path
        return self

    def get_path(self):
        return self.raw['path'] if 'path' in self.raw else None

    def set_username(self, username):
        self.raw['username'] = username
        return self

    def get_username(self):
        return self.raw['username'] if 'username' in self.raw else None

    def set_password(self, password):
        self.raw['password'] = password
        return self

    def set_time_identifier(self, time_identifier):
        self.raw['timeIdentifier'] = time_identifier
        return self

    def get_time_identifier(self):
        return self.raw['timeIdentifier'] if 'timeIdentifier' in self.raw else None

    def set_time_format(self, time_format):
        self.raw['timeFormat'] = time_format
        return self

    def get_time_format(self):
        return self.raw['timeFormat'] if 'timeFormat' in self.raw else None

    def set_streaming(self, streaming):
        self.raw['streaming'] = streaming
        return self

    def get_streaming(self):
        return self.raw['streaming'] if 'streaming' in self.raw else True

    def get_signals_tag_field(self):
        return self.raw['signalsTagField'] if 'signalsTagField' in self.raw else None

    def get_signals_delimiter(self):
        return self.raw['signalsDelimiter'] if 'signalsDelimiter' in self.raw else None

    def get_signals_location(self):
        return self.raw['signalsLocation'] if 'signalsLocation' in self.raw else None

    def get_value_column(self):
        return self.raw['valueColumn'] if 'valueColumn' in self.raw else None

    def to_json(self):
        return json.dumps(self.raw)
