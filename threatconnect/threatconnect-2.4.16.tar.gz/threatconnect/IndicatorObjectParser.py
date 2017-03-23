from collections import OrderedDict
from Config.ResourceType import ResourceType

from SharedMethods import get_resource_type
from IndicatorObject import IndicatorObject
from IndicatorObjectAdvanced import IndicatorObjectAdvanced
from RequestObject import RequestObject
from AttributeObject import parse_attribute
from TagObject import parse_tag

from IndicatorObjectTyped import (AddressIndicatorObject,
                                  CustomIndicatorObject,
                                  EmailAddressIndicatorObject,
                                  FileIndicatorObject,
                                  HostIndicatorObject,
                                  UrlIndicatorObject,)


def parse_base_indicator(indicator_dict, indicators_regex=None):
    """ """
    # indicator object
    indicator = IndicatorObject()


    #
    # standard values
    #
    indicator.set_date_added(indicator_dict['dateAdded'])
    indicator.set_id(indicator_dict['id'])
    indicator.set_last_modified(indicator_dict['lastModified'])
    indicator.set_weblink(indicator_dict['webLink'])

    #
    # optional values
    #
    if 'type' in indicator_dict:
        indicator.set_type(indicator_dict['type'])  # set type before indicator

    if 'confidence' in indicator_dict:
        indicator.set_confidence(indicator_dict['confidence'], update=False)
    if 'description' in indicator_dict:
        indicator.set_description(indicator_dict['description'], update=False)
    if 'owner' in indicator_dict:  # nested owner for single indicator result
        indicator.set_owner_name(indicator_dict['owner']['name'])
    if 'ownerName' in indicator_dict:
        indicator.set_owner_name(indicator_dict['ownerName'])
    if 'rating' in indicator_dict:
        indicator.set_rating(indicator_dict['rating'], update=False)

    if 'threatAssessConfidence' in indicator_dict:
        indicator.set_threat_assess_confidence(indicator_dict['threatAssessConfidence'])
    if 'threatAssessRating' in indicator_dict:
        indicator.set_threat_assess_rating(indicator_dict['threatAssessRating'])

    return indicator


def parse_typed_indicator(indicator_dict, resource_obj=None, api_filter=None,
                          request_uri=None, indicators_regex=None, indicator_parser=None):
    indicator = parse_base_indicator(indicator_dict, indicators_regex=indicators_regex)

    # Get the correct type and instantiate it

    #
    # address
    #
    if 'ip' in indicator_dict:
        indicator = AddressIndicatorObject(indicator)
        indicator.set_indicator(indicator_dict['ip'])
        if indicator.type is None:
            indicator.set_type('Address')  # set type before indicator

    #
    # email address
    #
    elif 'address' in indicator_dict:
        indicator = EmailAddressIndicatorObject(indicator)
        indicator.set_indicator(indicator_dict['address'])
        if indicator.type is None:
            indicator.set_type('EmailAddress')  # set type before indicator

    #
    # files
    #
    elif any(x for x in ['md5', 'sha1', 'sha256'] if x in indicator_dict):
        indicator = FileIndicatorObject(indicator)

        if 'md5' in indicator_dict:
            indicator.set_indicator(indicator_dict['md5'])
            if indicator.type is None:
                indicator.set_type('File')  # set type before indicator

        if 'sha1' in indicator_dict:
            indicator.set_indicator(indicator_dict['sha1'])
            if indicator.type is None:
                indicator.set_type('File')  # set type before indicator

        if 'sha256' in indicator_dict:
            indicator.set_indicator(indicator_dict['sha256'])
            if indicator.type is None:
                indicator.set_type('File')  # set type before indicator

        if 'size' in indicator_dict:
            indicator.set_size(indicator_dict['size'], update=False)

    #
    # hosts
    #
    elif any(x for x in ['hostName', 'dnsActive', 'whoisActive'] if x in indicator_dict):
        indicator = HostIndicatorObject(indicator)
        if 'hostName' in indicator_dict:
            indicator.set_indicator(indicator_dict['hostName'], ResourceType.HOSTS)
            if indicator.type is None:
                indicator.set_type('Host')  # set type before indicator

        if 'dnsActive' in indicator_dict:
            indicator.set_dns_active(indicator_dict['dnsActive'], update=False)

        if 'whoisActive' in indicator_dict:
            indicator.set_whois_active(indicator_dict['whoisActive'], update=False)

    #
    # urls
    #
    elif any(x for x in ['text', 'source'] if x in indicator_dict):
        indicator = UrlIndicatorObject(indicator)
        if 'text' in indicator_dict:
            indicator.set_indicator(indicator_dict['text'], ResourceType.URLS)

        if 'source' in indicator_dict:
            indicator.set_source(indicator_dict['source'], update=False)

    #
    # summmary means we got all indicators
    #
    elif 'summary' in indicator_dict and indicator.indicator is None:
        indicator_val = indicator_dict.get('summary')
        resource_type = get_resource_type(indicators_regex, indicator_val)
        if indicator.resource_type == ResourceType.CUSTOM_INDICATORS:
            indicator = CustomIndicatorObject(indicator)

            # summary comes in as a colon delimited string; we don't want that
            _type = indicator_dict.get('type', None)
            if _type is None or indicator_parser is None:
                raise AttributeError("No type found for Custom Indicator during initialization")

            custom_indicator_type = indicator_parser.get_custom_indicator_type_by_name(_type)
            if custom_indicator_type is None:
                raise AttributeError("Type is not currently supported for Custom Indicator initialization: {}".format(_type))

            indicator.set_api_entity(custom_indicator_type.api_entity)
            indicator.set_api_branch(custom_indicator_type.api_branch)

            # get the type and field names, then check the dict for those names
            field_names = indicator_parser.get_field_labels(custom_indicator_type)
            field_values = indicator_val.split(" : ")
            custom_fields = OrderedDict()
            for i in range(0, len(field_names)):
                custom_fields[field_names[i]]=field_values[i]
                # custom_field = CustomIndicatorField(field_names[i], value=field_values[i])
                # indicator.add_custom_fields(custom_field)
            indicator.set_custom_fields(custom_fields)
            indicator.set_indicator(custom_fields)
        else:
            resource_type = indicator.resource_type
            cls = {
                ResourceType.ADDRESSES: AddressIndicatorObject,
                ResourceType.CUSTOM_INDICATORS: CustomIndicatorObject,
                ResourceType.EMAIL_ADDRESSES: EmailAddressIndicatorObject,
                ResourceType.FILES: FileIndicatorObject,
                ResourceType.HOSTS: HostIndicatorObject,
                ResourceType.URLS: UrlIndicatorObject
            }
            typed_indicator = cls.get(resource_type)() if resource_type in cls else None
            typed_indicator.copy_slots(indicator)
            indicator = typed_indicator
            indicator.set_indicator(indicator_dict['summary'], resource_type)

    #
    # custom indicators
    #
    else:
        indicator = CustomIndicatorObject(indicator)
        # type MUST exist as well as tc_obj for us to continue
        _type = indicator_dict.get('type', None)
        if _type is None or indicator_parser is None:
            raise AttributeError("No type found for Custom Indicator during initialization")

        custom_indicator_type = indicator_parser.get_custom_indicator_type_by_name(_type)
        if custom_indicator_type is None:
            raise AttributeError("Type is not currently supported for Custom Indicator initialization: {}".format(_type))

        indicator.set_api_entity(custom_indicator_type.api_entity)
        indicator.set_api_branch(custom_indicator_type.api_branch)
        # get the type and field names, then check the dict for those names
        field_names = indicator_parser.get_field_labels(custom_indicator_type)
        custom_fields = OrderedDict()
        for field_name in field_names:
            field_val = "{0!s}".format(indicator_dict.get(field_name)).strip()
            custom_fields[field_name] = field_val
        indicator.set_custom_fields(custom_fields)
        indicator.set_indicator(custom_fields)


    #
    # attributes
    #
    if 'attribute' in indicator_dict:
        for attribute_dict in indicator_dict['attribute']:
            attribute = parse_attribute(attribute_dict, indicator)
            indicator.add_attribute(attribute)

    #
    # tag
    #
    if 'tag' in indicator_dict:
        for tag_dict in indicator_dict['tag']:
            tag = parse_tag(tag_dict)
            indicator.add_tag(tag)

    #
    # observations
    #
    if 'observationCount' in indicator_dict:
        indicator.set_observation_count(indicator_dict['observationCount'])

    if 'lastObserved' in indicator_dict:
        indicator.set_last_observed(indicator_dict['last_observed'])


    #
    # handle both resource containers and individual objects
    #
    if resource_obj is not None:
        # and not isinstance(resource_obj, IndicatorObjectAdvanced):
        # store the resource object in the master resource object list
        # must be submitted after parameters are set for indexing to work
        roi = resource_obj.add_master_resource_obj(indicator, indicator_dict['id'])

        # BCS - This causes a bug on searching for a single indicator over multiple
        #       owners, only 1 indicator is returned.
        # roi = resource_obj.add_master_resource_obj(indicator, indicator.indicator)

        # retrieve the resource object and update data
        return resource_obj.get_resource_by_identity(roi)

    #
    # filter (set after retrieving stored object)
    #
    if api_filter is not None:
        indicator.add_matched_filter(api_filter)

    #
    # request_uri (set after retrieving stored object)
    #
    if request_uri is not None:
        indicator.add_request_uri(request_uri)

    return indicator

class CustomIndicatorField(object):
    __slots__ = (
        '_label',
        # '_value',
        '_type'
    )

    def __init__(self, label, type=None):
        self._label = label
        # self._value = value
        self._type = type

    @property
    def label(self):
        return self._label

    # @property
    # def value(self):
    #     return self._value

    @property
    def type(self):
        return self._type

class CustomIndicatorType(object):
    __slots__ = (
        '_name',
        '_parsable',
        '_api_branch',
        '_api_entity',
        '_fields',
        '_case_preference'
    )

    def __init__(self, name=None, parsable=False, api_branch=None, api_entity=None, fields=None, case_preference="LOWER"):
        self._name = name
        self._parsable = parsable
        self._api_branch = api_branch
        self._api_entity = api_entity
        self._fields = []
        if fields is not None:
            self._fields = fields if isinstance(fields, list) else [fields]
        self._case_preference = case_preference

    @property
    def name(self):
        return self._name

    # def set_name(self, data):
    #     self._name = data

    @property
    def parsable(self):
        return self._parsable

    # def set_parsable(self, data):
    #     self._parsable = data

    @property
    def api_branch(self):
        return self._api_branch

    # def set_api_branch(self, data):
    #     self._api_branch = data

    @property
    def api_entity(self):
        return self._api_entity

    # def set_api_entity(self, data):
    #     self._api_entity = data

    @property
    def fields(self):
        return self._fields

    # def set_fields(self, data):
    #     self._fields = data

    @property
    def case_preference(self):
        return self._case_preference

    # def set_case_preference(self, data):
    #     self._case_preference = data


class IndicatorObjectParser(object):

    def __init__(self, tc_obj):
        self._tc = tc_obj

    def init(self):
        """Adding second init process to allow proxies to be set before requesting IndicatorTypes"""
        self._custom_indicator_types = self._get_custom_types_from_api()

    @property
    def tc(self):
        return self._tc

    @property
    def custom_indicator_types(self):
        return self._custom_indicator_types

    def _get_custom_types_from_api(self):

        ro = RequestObject()

        ro.set_http_method('GET')
        ro.set_request_uri('/v2/types/indicatorTypes')
        ro.set_owner_allowed(False)
        ro.set_resource_pagination(True)
        self.tc._api_request_headers(ro)

        api_resp = self.tc.api_request(ro)
        json = api_resp.json()
        types = []

        if json.get('data', None) is not None:
            for indicator_type in json['data']['indicatorType']:
                if indicator_type.get('custom', 'false') == 'true':
                    field_names_with_nones = [indicator_type.get('value{0!s}Label'.format(i), None) for i in range(1, 4)]
                    field_names = [field_name for field_name in field_names_with_nones if field_name]

                    field_types_with_nones = [indicator_type.get('value{0!s}Type'.format(i), None) for i in range(1, 4)]
                    field_types = [field_type for field_type in field_types_with_nones if field_type]

                    fields = []
                    for i in range(0, len(field_names)):
                        fields.append(CustomIndicatorField(field_names[i], type=field_types[i]))

                    types.append(CustomIndicatorType(
                        name=indicator_type.get('name'),
                        api_entity=indicator_type.get('apiEntity'),
                        api_branch=indicator_type.get('apiBranch'),
                        parsable=indicator_type.get('parsable'),
                        fields=fields,
                        case_preference=indicator_type.get('casePreference', None)
                    ))

        return types

    @property
    def custom_indicator_types(self):
        return self._custom_indicator_types

    def get_custom_indicator_type_by_api_entity(self, api_entity):
        for custom_indicator_type in self.custom_indicator_types:
            if custom_indicator_type.api_entity == api_entity:
                return custom_indicator_type
        return None

    def exists_api_entity_in_custom_indicator_types(self, api_entity):
        return self.get_custom_indicator_type_by_api_entity(api_entity) is None

    def get_field_labels_by_api_entity(self, api_entity):
        """ gets the fields for a given custom indicator's name (name is type in the json returned by the API)"""
        fields = self.get_custom_indicator_type_by_api_entity(api_entity).fields
        return [field.label for field in fields]

    def get_custom_indicator_type_by_name(self, name):
        for custom_indicator_type in self.custom_indicator_types:
            if custom_indicator_type.name == name:
                return custom_indicator_type
        return None

    def exists_name_in_custom_indicator_types(self, name):
        return self.get_custom_indicator_type_by_name(name) is None

    def get_field_labels_by_name(self, type):
        """ gets the fields for a given custom indicator's name (name is "type" in the json returned by the API)"""
        fields = self.get_custom_indicator_type_by_name(type).fields
        return [field.label for field in fields]

    def get_field_labels(self, custom_indicator_type):
        return [field.label for field in custom_indicator_type.fields]

    def construct_typed_indicator(self, resource_type, api_entity=None):
        cls = {
            ResourceType.ADDRESSES: AddressIndicatorObject,
            ResourceType.CUSTOM_INDICATORS: CustomIndicatorObject,
            ResourceType.EMAIL_ADDRESSES: EmailAddressIndicatorObject,
            ResourceType.FILES: FileIndicatorObject,
            ResourceType.HOSTS: HostIndicatorObject,
            ResourceType.URLS: UrlIndicatorObject
        }
        indicator = cls.get(resource_type)() if resource_type in cls else None
        if api_entity is not None and indicator is not None:
            indicator.set_custom_type(api_entity)

            custom_i_type = self.get_custom_indicator_type_by_api_entity(api_entity)
            if custom_i_type is None:
                raise AttributeError('No Custom Indicator data available for api_entity: {}'.format(api_entity))

            indicator.set_api_branch(custom_i_type.api_branch)
            indicator.set_api_entity(custom_i_type.api_entity)
        return indicator

    def construct_typed_advanced_indicator(self, resource_container, resource_obj):
        """ Creates IndicatorObject of the correct type (assuming resource_obj has its type)"""
        resource_type = resource_obj.resource_type
        typed_resource_obj = self.construct_typed_indicator(resource_type).copy_slots(resource_obj)

        return IndicatorObjectAdvanced(self.tc, resource_container, typed_resource_obj, api_entity=resource_obj.api_entity)