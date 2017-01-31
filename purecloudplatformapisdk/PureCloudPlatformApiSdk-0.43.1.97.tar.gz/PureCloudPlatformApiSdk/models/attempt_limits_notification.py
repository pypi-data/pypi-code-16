# coding: utf-8

"""
Copyright 2016 SmartBear Software

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Ref: https://github.com/swagger-api/swagger-codegen
"""

from pprint import pformat
from six import iteritems
import re


class AttemptLimitsNotification(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        AttemptLimitsNotification - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'name': 'str',
            'date_created': 'datetime',
            'date_modified': 'datetime',
            'version': 'int',
            'max_attempts_per_contact': 'int',
            'max_attempts_per_number': 'int',
            'time_zone_id': 'str',
            'reset_period': 'str',
            'recall_entries': 'dict(str, AttemptLimitsNotificationRecallEntries)',
            'breadth_first_recalls': 'bool',
            'additional_properties': 'object'
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'date_created': 'dateCreated',
            'date_modified': 'dateModified',
            'version': 'version',
            'max_attempts_per_contact': 'maxAttemptsPerContact',
            'max_attempts_per_number': 'maxAttemptsPerNumber',
            'time_zone_id': 'timeZoneId',
            'reset_period': 'resetPeriod',
            'recall_entries': 'recallEntries',
            'breadth_first_recalls': 'breadthFirstRecalls',
            'additional_properties': 'additionalProperties'
        }

        self._id = None
        self._name = None
        self._date_created = None
        self._date_modified = None
        self._version = None
        self._max_attempts_per_contact = None
        self._max_attempts_per_number = None
        self._time_zone_id = None
        self._reset_period = None
        self._recall_entries = None
        self._breadth_first_recalls = None
        self._additional_properties = None

    @property
    def id(self):
        """
        Gets the id of this AttemptLimitsNotification.


        :return: The id of this AttemptLimitsNotification.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this AttemptLimitsNotification.


        :param id: The id of this AttemptLimitsNotification.
        :type: str
        """
        
        self._id = id

    @property
    def name(self):
        """
        Gets the name of this AttemptLimitsNotification.


        :return: The name of this AttemptLimitsNotification.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this AttemptLimitsNotification.


        :param name: The name of this AttemptLimitsNotification.
        :type: str
        """
        
        self._name = name

    @property
    def date_created(self):
        """
        Gets the date_created of this AttemptLimitsNotification.


        :return: The date_created of this AttemptLimitsNotification.
        :rtype: datetime
        """
        return self._date_created

    @date_created.setter
    def date_created(self, date_created):
        """
        Sets the date_created of this AttemptLimitsNotification.


        :param date_created: The date_created of this AttemptLimitsNotification.
        :type: datetime
        """
        
        self._date_created = date_created

    @property
    def date_modified(self):
        """
        Gets the date_modified of this AttemptLimitsNotification.


        :return: The date_modified of this AttemptLimitsNotification.
        :rtype: datetime
        """
        return self._date_modified

    @date_modified.setter
    def date_modified(self, date_modified):
        """
        Sets the date_modified of this AttemptLimitsNotification.


        :param date_modified: The date_modified of this AttemptLimitsNotification.
        :type: datetime
        """
        
        self._date_modified = date_modified

    @property
    def version(self):
        """
        Gets the version of this AttemptLimitsNotification.


        :return: The version of this AttemptLimitsNotification.
        :rtype: int
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Sets the version of this AttemptLimitsNotification.


        :param version: The version of this AttemptLimitsNotification.
        :type: int
        """
        
        self._version = version

    @property
    def max_attempts_per_contact(self):
        """
        Gets the max_attempts_per_contact of this AttemptLimitsNotification.


        :return: The max_attempts_per_contact of this AttemptLimitsNotification.
        :rtype: int
        """
        return self._max_attempts_per_contact

    @max_attempts_per_contact.setter
    def max_attempts_per_contact(self, max_attempts_per_contact):
        """
        Sets the max_attempts_per_contact of this AttemptLimitsNotification.


        :param max_attempts_per_contact: The max_attempts_per_contact of this AttemptLimitsNotification.
        :type: int
        """
        
        self._max_attempts_per_contact = max_attempts_per_contact

    @property
    def max_attempts_per_number(self):
        """
        Gets the max_attempts_per_number of this AttemptLimitsNotification.


        :return: The max_attempts_per_number of this AttemptLimitsNotification.
        :rtype: int
        """
        return self._max_attempts_per_number

    @max_attempts_per_number.setter
    def max_attempts_per_number(self, max_attempts_per_number):
        """
        Sets the max_attempts_per_number of this AttemptLimitsNotification.


        :param max_attempts_per_number: The max_attempts_per_number of this AttemptLimitsNotification.
        :type: int
        """
        
        self._max_attempts_per_number = max_attempts_per_number

    @property
    def time_zone_id(self):
        """
        Gets the time_zone_id of this AttemptLimitsNotification.


        :return: The time_zone_id of this AttemptLimitsNotification.
        :rtype: str
        """
        return self._time_zone_id

    @time_zone_id.setter
    def time_zone_id(self, time_zone_id):
        """
        Sets the time_zone_id of this AttemptLimitsNotification.


        :param time_zone_id: The time_zone_id of this AttemptLimitsNotification.
        :type: str
        """
        
        self._time_zone_id = time_zone_id

    @property
    def reset_period(self):
        """
        Gets the reset_period of this AttemptLimitsNotification.


        :return: The reset_period of this AttemptLimitsNotification.
        :rtype: str
        """
        return self._reset_period

    @reset_period.setter
    def reset_period(self, reset_period):
        """
        Sets the reset_period of this AttemptLimitsNotification.


        :param reset_period: The reset_period of this AttemptLimitsNotification.
        :type: str
        """
        allowed_values = ["NEVER", "TODAY"]
        if reset_period.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for reset_period -> " + reset_period
            self._reset_period = "outdated_sdk_version"
        else:
            self._reset_period = reset_period.lower()

    @property
    def recall_entries(self):
        """
        Gets the recall_entries of this AttemptLimitsNotification.


        :return: The recall_entries of this AttemptLimitsNotification.
        :rtype: dict(str, AttemptLimitsNotificationRecallEntries)
        """
        return self._recall_entries

    @recall_entries.setter
    def recall_entries(self, recall_entries):
        """
        Sets the recall_entries of this AttemptLimitsNotification.


        :param recall_entries: The recall_entries of this AttemptLimitsNotification.
        :type: dict(str, AttemptLimitsNotificationRecallEntries)
        """
        
        self._recall_entries = recall_entries

    @property
    def breadth_first_recalls(self):
        """
        Gets the breadth_first_recalls of this AttemptLimitsNotification.


        :return: The breadth_first_recalls of this AttemptLimitsNotification.
        :rtype: bool
        """
        return self._breadth_first_recalls

    @breadth_first_recalls.setter
    def breadth_first_recalls(self, breadth_first_recalls):
        """
        Sets the breadth_first_recalls of this AttemptLimitsNotification.


        :param breadth_first_recalls: The breadth_first_recalls of this AttemptLimitsNotification.
        :type: bool
        """
        
        self._breadth_first_recalls = breadth_first_recalls

    @property
    def additional_properties(self):
        """
        Gets the additional_properties of this AttemptLimitsNotification.


        :return: The additional_properties of this AttemptLimitsNotification.
        :rtype: object
        """
        return self._additional_properties

    @additional_properties.setter
    def additional_properties(self, additional_properties):
        """
        Sets the additional_properties of this AttemptLimitsNotification.


        :param additional_properties: The additional_properties of this AttemptLimitsNotification.
        :type: object
        """
        
        self._additional_properties = additional_properties

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other

