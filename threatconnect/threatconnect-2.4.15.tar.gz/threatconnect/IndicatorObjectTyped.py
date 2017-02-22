from collections import OrderedDict

from SharedMethods import get_hash_type, uni, urlsafe
from Config.ResourceType import ResourceType
from IndicatorObject import IndicatorObject


class AddressIndicatorObject(IndicatorObject):
    __slots__ = ()

    def __init__(self, obj_from=None):
        super(AddressIndicatorObject, self).__init__()
        if obj_from is not None:
            self.copy_slots(obj_from)
        self._set_resource_type(ResourceType.ADDRESSES)

    # def set_indicator(self, data, resource_type=None, update=True):
    #     self._ip = uni(data)
    #     self._reference_indicator = urlsafe(self._ip)
    #
    #     # additional resource type specific attributes
    #     self._properties['_ip'] = {
    #         'api_field': 'ip',
    #         'method': 'set_indicator',
    #         'required': True,
    #     }

    #
    #   Read-Only
    #
    @property
    def indicator(self):
        return self._ip


class EmailAddressIndicatorObject(IndicatorObject):
    __slots__ = ()

    def __init__(self, obj_from=None):
        super(EmailAddressIndicatorObject, self).__init__()
        if obj_from is not None:
            self.copy_slots(obj_from)
        self._set_resource_type(ResourceType.EMAIL_ADDRESSES)
    #
    # def set_indicator(self, data, resource_type=None, update=True):
    #     self._address = uni(data)
    #     self._reference_indicator = urlsafe(self._address)
    #
    #     # additional resource type specific attributes
    #     self._properties['_address'] = {
    #         'api_field': 'address',
    #         'method': 'set_indicator',
    #         'required': True,
    #     }

    @property
    def indicator(self):
        return self._address


class FileIndicatorObject(IndicatorObject):
    __slots__ = ()

    def __init__(self, obj_from=None):
        super(FileIndicatorObject, self).__init__()
        if obj_from is not None:
            self.copy_slots(obj_from)
        self._set_resource_type(ResourceType.FILES)

    # def set_indicator(self, data, resource_type=None, update=True):
    #     # handle different hash type
    #     hash_type = get_hash_type(data)
    #     if hash_type == 'MD5':
    #         self._md5 = data
    #         if self._reference_indicator is None:  # reference indicator for attr, tag, etc adds
    #             self._reference_indicator = urlsafe(self._md5)
    #     elif hash_type == 'SHA1':
    #         self._sha1 = data
    #         if self._reference_indicator is None:  # reference indicator for attr, tag, etc adds
    #             self._reference_indicator = urlsafe(self._sha1)
    #     elif hash_type == 'SHA256':
    #         self._sha256 = data
    #         if self._reference_indicator is None:  # reference indicator for attr, tag, etc adds
    #             self._reference_indicator = urlsafe(self._sha256)
    #
    #     self._properties['_md5'] = {
    #         'api_field': 'md5',
    #         'method': 'set_indicator',
    #         'required': True,
    #     }
    #     self._properties['_sha1'] = {
    #         'api_field': 'sha1',
    #         'method': 'set_indicator',
    #         'required': True,
    #     }
    #     self._properties['_sha256'] = {
    #         'api_field': 'sha256',
    #         'method': 'set_indicator',
    #         'required': True,
    #     }
    #     self._properties['_size'] = {
    #         'api_field': 'size',
    #         'method': 'set_size',
    #         'required': False,
    #     }
    #
    #     if update and self._phase == 0:
    #         self._phase = 2

    @property
    def indicator(self):
        return {
            'md5': self._md5,
            'sha1': self._sha1,
            'sha256': self._sha256
        }


class HostIndicatorObject(IndicatorObject):
    __slots__ = ()

    def __init__(self, obj_from=None):
        super(HostIndicatorObject, self).__init__()
        if obj_from is not None:
            self.copy_slots(obj_from)
        self._set_resource_type(ResourceType.HOSTS)

    # def set_indicator(self, data, resource_type=None, update=True):
    #     self._hostname = uni(data)
    #     self._reference_indicator = urlsafe(self._hostname)
    #
    #     # additional resource type specific attributes
    #     self._properties['_hostname'] = {
    #         'api_field': 'hostName',
    #         'method': 'set_indicator',
    #         'required': True,
    #     }
    #     self._properties['_dns_active'] = {
    #         'api_field': 'dnsActive',
    #         'method': 'set_dns_active',
    #         'required': False,
    #     }
    #     self._properties['_whois_active'] = {
    #         'api_field': 'whoisActive',
    #         'method': 'set_whois_active',
    #         'required': False,
    #     }

    @property
    def indicator(self):
        return self._hostname


class UrlIndicatorObject(IndicatorObject):
    __slots__ = ()

    def __init__(self, obj_from=None):
        super(UrlIndicatorObject, self).__init__()
        if obj_from is not None:
            self.copy_slots(obj_from)
        self._set_resource_type(ResourceType.URLS)

    # def set_indicator(self, data, resource_type=None, update=True):
    #     self._text = uni(data)
    #     self._reference_indicator = urlsafe(self._text)
    #
    #     # additional resource type specific attributes
    #     self._properties['_text'] = {
    #         'api_field': 'text',
    #         'method': 'set_indicator',
    #         'required': True,
    #     }

    @property
    def indicator(self):
        return self._text


class CustomIndicatorObject(IndicatorObject):
    __slots__ = ()

    def __init__(self, obj_from=None):
        super(CustomIndicatorObject, self).__init__()
        if obj_from is not None:
            self.copy_slots(obj_from)
        self._set_resource_type(ResourceType.CUSTOM_INDICATORS)

    # def set_indicator(self, data, resource_type=None, update=True, field_names=None):
    #     # make sure they're in the right order
    #     if not isinstance(data, OrderedDict):
    #         raise AttributeError("Custom Indicator must be an OrderedDict")
    #
    #     self._custom_fields = uni(data)
    #     self._reference_indicator = urlsafe(' : '.join(self._custom_fields.values()))
    #
    #     # additional resource type specific attributes
    #     self._properties['_custom_fields'] = {
    #         'api_field': self.api_entity,
    #         'method': 'set_indicator',
    #         'required': True,
    #     }

    @property
    def indicator(self):
        """
        returns custom indicator as an OrderedDict of 1-3 fields
        which when delimited represent the indicator
        """

        return self._custom_fields

