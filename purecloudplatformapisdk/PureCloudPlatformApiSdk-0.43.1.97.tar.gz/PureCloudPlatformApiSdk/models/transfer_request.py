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


class TransferRequest(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        TransferRequest - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'user_id': 'str',
            'address': 'str',
            'user_name': 'str',
            'queue_id': 'str',
            'voicemail': 'bool'
        }

        self.attribute_map = {
            'user_id': 'userId',
            'address': 'address',
            'user_name': 'userName',
            'queue_id': 'queueId',
            'voicemail': 'voicemail'
        }

        self._user_id = None
        self._address = None
        self._user_name = None
        self._queue_id = None
        self._voicemail = None

    @property
    def user_id(self):
        """
        Gets the user_id of this TransferRequest.
        The user ID of the transfer target.

        :return: The user_id of this TransferRequest.
        :rtype: str
        """
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        """
        Sets the user_id of this TransferRequest.
        The user ID of the transfer target.

        :param user_id: The user_id of this TransferRequest.
        :type: str
        """
        
        self._user_id = user_id

    @property
    def address(self):
        """
        Gets the address of this TransferRequest.
        The phone number or address of the transfer target.

        :return: The address of this TransferRequest.
        :rtype: str
        """
        return self._address

    @address.setter
    def address(self, address):
        """
        Sets the address of this TransferRequest.
        The phone number or address of the transfer target.

        :param address: The address of this TransferRequest.
        :type: str
        """
        
        self._address = address

    @property
    def user_name(self):
        """
        Gets the user_name of this TransferRequest.
        The user name of the transfer target.

        :return: The user_name of this TransferRequest.
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """
        Sets the user_name of this TransferRequest.
        The user name of the transfer target.

        :param user_name: The user_name of this TransferRequest.
        :type: str
        """
        
        self._user_name = user_name

    @property
    def queue_id(self):
        """
        Gets the queue_id of this TransferRequest.
        The queue ID of the transfer target.

        :return: The queue_id of this TransferRequest.
        :rtype: str
        """
        return self._queue_id

    @queue_id.setter
    def queue_id(self, queue_id):
        """
        Sets the queue_id of this TransferRequest.
        The queue ID of the transfer target.

        :param queue_id: The queue_id of this TransferRequest.
        :type: str
        """
        
        self._queue_id = queue_id

    @property
    def voicemail(self):
        """
        Gets the voicemail of this TransferRequest.
        If true, then transfer to the user's voicemail.

        :return: The voicemail of this TransferRequest.
        :rtype: bool
        """
        return self._voicemail

    @voicemail.setter
    def voicemail(self, voicemail):
        """
        Sets the voicemail of this TransferRequest.
        If true, then transfer to the user's voicemail.

        :param voicemail: The voicemail of this TransferRequest.
        :type: bool
        """
        
        self._voicemail = voicemail

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

