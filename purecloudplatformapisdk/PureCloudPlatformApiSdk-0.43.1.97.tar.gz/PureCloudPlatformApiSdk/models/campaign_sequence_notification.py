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


class CampaignSequenceNotification(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        CampaignSequenceNotification - a model defined in Swagger

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
            'campaigns': 'list[DocumentDataV2NotificationCreatedBy]',
            'current_campaign': 'int',
            'status': 'str',
            'stop_message': 'str',
            'repeat': 'bool',
            'additional_properties': 'object'
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'date_created': 'dateCreated',
            'date_modified': 'dateModified',
            'version': 'version',
            'campaigns': 'campaigns',
            'current_campaign': 'currentCampaign',
            'status': 'status',
            'stop_message': 'stopMessage',
            'repeat': 'repeat',
            'additional_properties': 'additionalProperties'
        }

        self._id = None
        self._name = None
        self._date_created = None
        self._date_modified = None
        self._version = None
        self._campaigns = None
        self._current_campaign = None
        self._status = None
        self._stop_message = None
        self._repeat = None
        self._additional_properties = None

    @property
    def id(self):
        """
        Gets the id of this CampaignSequenceNotification.


        :return: The id of this CampaignSequenceNotification.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this CampaignSequenceNotification.


        :param id: The id of this CampaignSequenceNotification.
        :type: str
        """
        
        self._id = id

    @property
    def name(self):
        """
        Gets the name of this CampaignSequenceNotification.


        :return: The name of this CampaignSequenceNotification.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this CampaignSequenceNotification.


        :param name: The name of this CampaignSequenceNotification.
        :type: str
        """
        
        self._name = name

    @property
    def date_created(self):
        """
        Gets the date_created of this CampaignSequenceNotification.


        :return: The date_created of this CampaignSequenceNotification.
        :rtype: datetime
        """
        return self._date_created

    @date_created.setter
    def date_created(self, date_created):
        """
        Sets the date_created of this CampaignSequenceNotification.


        :param date_created: The date_created of this CampaignSequenceNotification.
        :type: datetime
        """
        
        self._date_created = date_created

    @property
    def date_modified(self):
        """
        Gets the date_modified of this CampaignSequenceNotification.


        :return: The date_modified of this CampaignSequenceNotification.
        :rtype: datetime
        """
        return self._date_modified

    @date_modified.setter
    def date_modified(self, date_modified):
        """
        Sets the date_modified of this CampaignSequenceNotification.


        :param date_modified: The date_modified of this CampaignSequenceNotification.
        :type: datetime
        """
        
        self._date_modified = date_modified

    @property
    def version(self):
        """
        Gets the version of this CampaignSequenceNotification.


        :return: The version of this CampaignSequenceNotification.
        :rtype: int
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Sets the version of this CampaignSequenceNotification.


        :param version: The version of this CampaignSequenceNotification.
        :type: int
        """
        
        self._version = version

    @property
    def campaigns(self):
        """
        Gets the campaigns of this CampaignSequenceNotification.


        :return: The campaigns of this CampaignSequenceNotification.
        :rtype: list[DocumentDataV2NotificationCreatedBy]
        """
        return self._campaigns

    @campaigns.setter
    def campaigns(self, campaigns):
        """
        Sets the campaigns of this CampaignSequenceNotification.


        :param campaigns: The campaigns of this CampaignSequenceNotification.
        :type: list[DocumentDataV2NotificationCreatedBy]
        """
        
        self._campaigns = campaigns

    @property
    def current_campaign(self):
        """
        Gets the current_campaign of this CampaignSequenceNotification.


        :return: The current_campaign of this CampaignSequenceNotification.
        :rtype: int
        """
        return self._current_campaign

    @current_campaign.setter
    def current_campaign(self, current_campaign):
        """
        Sets the current_campaign of this CampaignSequenceNotification.


        :param current_campaign: The current_campaign of this CampaignSequenceNotification.
        :type: int
        """
        
        self._current_campaign = current_campaign

    @property
    def status(self):
        """
        Gets the status of this CampaignSequenceNotification.


        :return: The status of this CampaignSequenceNotification.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this CampaignSequenceNotification.


        :param status: The status of this CampaignSequenceNotification.
        :type: str
        """
        allowed_values = ["ON", "OFF", "COMPLETE"]
        if status.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for status -> " + status
            self._status = "outdated_sdk_version"
        else:
            self._status = status.lower()

    @property
    def stop_message(self):
        """
        Gets the stop_message of this CampaignSequenceNotification.


        :return: The stop_message of this CampaignSequenceNotification.
        :rtype: str
        """
        return self._stop_message

    @stop_message.setter
    def stop_message(self, stop_message):
        """
        Sets the stop_message of this CampaignSequenceNotification.


        :param stop_message: The stop_message of this CampaignSequenceNotification.
        :type: str
        """
        
        self._stop_message = stop_message

    @property
    def repeat(self):
        """
        Gets the repeat of this CampaignSequenceNotification.


        :return: The repeat of this CampaignSequenceNotification.
        :rtype: bool
        """
        return self._repeat

    @repeat.setter
    def repeat(self, repeat):
        """
        Sets the repeat of this CampaignSequenceNotification.


        :param repeat: The repeat of this CampaignSequenceNotification.
        :type: bool
        """
        
        self._repeat = repeat

    @property
    def additional_properties(self):
        """
        Gets the additional_properties of this CampaignSequenceNotification.


        :return: The additional_properties of this CampaignSequenceNotification.
        :rtype: object
        """
        return self._additional_properties

    @additional_properties.setter
    def additional_properties(self, additional_properties):
        """
        Sets the additional_properties of this CampaignSequenceNotification.


        :param additional_properties: The additional_properties of this CampaignSequenceNotification.
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

