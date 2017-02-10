# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#


#    "descriptor" : {
#      "type" : "com.formationds.events.model.EventDescriptor",
#      "key" : "testservice.test_event",
#      "severity" : "CONFIG",
#      "categories" : [ "SERVICE", "USER" ],
#      "messageFormat" : "User $user$ configured the service $svc$",
#      "messageAttributeNames" : [ "user", "svc" ]
#    },
class EventDescriptor(object):

    def __init__(self, type="", key="", severity="", categories=None, message_format="", message_attribute_names=None):

        self._e_type = type
        self._key = key
        self._severity = severity
        self._message_format = message_format

        if categories is None:
            self._categories = []
        else:
            self._categories = categories

        if message_attribute_names is None:
            self._message_attribute_names = []
        else:
            self._message_attribute_names = message_attribute_names

    @property
    def e_type(self):
        return self._e_type

    @e_type.setter
    def e_type(self, value):
        self._e_type = value

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def severity(self):
        return self._severity

    @severity.setter
    def severity(self, value):
        self._severity = value

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, value):
        self._categories = value

    @property
    def message_format(self):
        return self._message_format

    @message_format.setter
    def message_format(self, value):
        self._message_format = value

    @property
    def message_attribute_names(self):
        return self._message_attribute_names

    @message_attribute_names.setter
    def message_attribute_names(self, value):
        self._message_attribute_names = value
