# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#

from enum import Enum, unique

import event_category
import event_severity
import event_type

# Sample server response:
#
# {
#  "type" : "com.formationds.events.model.FormattedEvent",
#  "event" : {
#    "type" : "com.formationds.events.model.Event",
#    "timestamp" : {'seconds': 1482447687, 'nanos': 488000000},
#    "descriptor" : {
#      "type" : "com.formationds.events.model.EventDescriptor",
#      "key" : "testservice.test_event",
#      "severity" : "CONFIG",
#      "categories" : [ "SERVICE", "USER" ],
#      "messageFormat" : "User $user$ configured the service $svc$",
#      "messageAttributeNames" : [ "user", "svc" ]
#    },
#    "sourceInfo" : {
#      "type" : "com.formationds.events.model.ServiceSource",
#      "id" : "1",
#      "nodeId" : 1000,
#      "nodeAddress" : "mynode.mydomain.com",
#      "pid" : 1234,
#      "processName" : "java blah blah",
#      "serviceId" : 1004,
#      "serviceType" : "OM",
#      "serviceVersion" : "0.1.0",
#      "attributes" : { }
#    },
#    "attributes" : {
#      "svc" : "X",
#      "user" : "Joe"
#    }
#  },
#  "locale" : null,
#  "eventMessage" : "User Joe configured the service X"
# }

# TODO: Can't add enumerated values in the Event object until server response is valid.
# categories, in new event model, are just a list of strings.

class Event(object):
    '''Represents a persisted event.

    Events are stored with a generated id, a timestamp, type, category, severity, and a state.
    The event details include a message key and arguments.

    Attributes
    ----------
    :type __uuid: long TODO

    :type __message_key: string
    :type __creation_time: long
    :type __default_message: string
    :type _source_info ``model.event.EventSourceInfo`` Information about the sender of the event

    :type __categories: ``model.event.EventCategory``  TODO
    :type __severity: ``model.event.EventSeverity``  TODO
    :type __event_type: ``model.event.EventType``          TODO
    '''

    def __init__(self, uuid=-1, message_key="", creation_time=0, default_message=None, severity=None, categories=None,
                 message_args=None, e_type=None, event_content=None, locale=None, event_message=""):


        # This prevents issues with using lists as default parameters in methods
        # e.g. : http://docs.python-guide.org/en/latest/writing/gotchas/#mutable-default-arguments
        if categories is None:
            categories = []

        # Working with key value pairs is much easier, so we'll pack whatever list we received in the dict
        # this way any additional args can be assigned with a k/v pair instead of simply relying on position in
        # the list
        if type(message_args) is None or type(message_args) is list:
            self.__message_args = {'listArgs': message_args}
        elif type(message_args) is dict:
            self.__message_args = message_args
        else:
            self.message_args = {}

        self.__message_key = message_key
        self.__uuid = uuid
        self.__creation_time = creation_time
        self.__default_message = default_message
        self.__categories = categories
        self.__severity = severity

        self.__type = e_type
        self.__event_content = event_content
        self.__locale = locale
        self.__event_message = event_message

    @property
    def message_key(self):
        return self.__message_key

    @message_key.setter
    def message_key(self, message_key):
        self.__message_key = message_key

    @property
    def creation_time(self):
        return self.__creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        self.__creation_time = creation_time

    @property
    def default_message(self):
        return self.__default_message

    @default_message.setter
    def default_message(self, default_message):
        self.__default_message = default_message

    @property
    def severity(self):
        return self.__severity

    @severity.setter
    def severity(self, severity):
        self.__severity = severity

    @property
    def categories(self):
        return self.__categories

    @categories.setter
    def categories(self, categories):
        self.__categories = categories

    @property
    def uuid(self):
        return self.__uuid

    @uuid.setter
    def uuid(self, uuid):
        self.__uuid = uuid

    @property
    def message_args(self):
        return self.__message_args

    @message_args.setter
    def message_args(self, value):
        if type(value) is list:
            self.__message_args = {'listArgs': value}
        elif type(value) is dict:
            self.__message_args = value
        else:
            self.__message_args = {}

    @property
    def e_type(self):
        return self.__type

    @e_type.setter
    def e_type(self, value):
        self.__type = value

    @property
    def event_content(self):
        return self.__event_content

    @event_content.setter
    def event_content(self, value):
        self.__event_content = value

    @property
    def locale(self):
        return self.__locale

    @locale.setter
    def locale(self, value):
        self.__locale = value

    @property
    def event_message(self):
        return self.__event_message

    @event_message.setter
    def event_message(self, value):
        self.__event_message = value


#"event" : {
#    "type" : "com.formationds.events.model.Event",
#    "timestamp" : 1482447687.488000000,
#    "descriptor" : {
#      "type" : "com.formationds.events.model.EventDescriptor",
#      "key" : "testservice.test_event",
#      "severity" : "CONFIG",
#      "categories" : [ "SERVICE", "USER" ],
#      "messageFormat" : "User $user$ configured the service $svc$",
#      "messageAttributeNames" : [ "user", "svc" ]
#    },
#    "sourceInfo" : {
#      "type" : "com.formationds.events.model.ServiceSource",
#      "id" : "1",
#      "nodeId" : 1000,
#      "nodeAddress" : "mynode.mydomain.com",
#      "pid" : 1234,
#      "processName" : "java blah blah",
#      "serviceId" : 1004,
#      "serviceType" : "OM",
#      "serviceVersion" : "0.1.0",
#      "attributes" : { }
#    },
#    "attributes" : {
#      "svc" : "X",
#      "user" : "Joe"
#    }
#  },
class EventContent(object):
    """
    Class to define the contents of an Event for the v9 REST endpoint
    """

    def __init__(self, e_type="", timestamp=None, descriptor=None, source_info=None, attributes=None):

        self.__type = e_type
        self.__timestamp = timestamp
        self.__descriptor = descriptor
        self.__source_info = source_info

        if timestamp is None:
            self.__timestamp = {'seconds': 0, 'nanos': 0}
        else:
            self.__timestamp = timestamp

        if attributes is None:
            self.__attributes = {}
        else:
            self.__attributes = attributes

    @property
    def e_type(self):
        return self.__type

    @e_type.setter
    def e_type(self, value):
        self.__type = value

    @property
    def timestamp(self):
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, value):
        self.__timestamp = value

    @property
    def source_info(self):
        return self.__source_info

    @source_info.setter
    def source_info(self, value):
        self.__source_info = value

    @property
    def descriptor(self):
        return self.__descriptor

    @descriptor.setter
    def descriptor(self, value):
        self.__descriptor = value

    @property
    def attributes(self):
        return self.__attributes

    @attributes.setter
    def attributes(self, value):
        self.__attributes = value
