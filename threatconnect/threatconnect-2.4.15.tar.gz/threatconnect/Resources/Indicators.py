""" standard """
import re
import types
import uuid

""" custom """
# parent classes
from collections import OrderedDict

from threatconnect import IndicatorFilterMethods
from threatconnect import SharedMethods

from threatconnect import ApiProperties
from threatconnect.Config.IndicatorType import IndicatorType
from threatconnect.Config.ResourceType import ResourceType
from threatconnect.ErrorCodes import ErrorCodes
from threatconnect.FilterObject import FilterObject
from threatconnect.SharedMethods import get_resource_type
from threatconnect.RequestObject import RequestObject
from threatconnect.Resource import Resource


class Indicators(Resource):
    """ """
    def __init__(self, tc_obj):
        """ """
        super(Indicators, self).__init__(tc_obj)

        self._filter_class = IndicatorFilterObject
        self._modified_since = None
        self._resource_type = ResourceType.INDICATORS

    def _method_wrapper(self, resource_object):
        """ return resource object as new object with additional methods """
        return self.tc.indicator_parser.construct_typed_advanced_indicator(self, resource_object)

    # def add_custom_type(self, api_entity, api_branch, name,
    #                     field1, field1_t='text', field2=None, field2_t=None, field3=None, field3_t=None):
    #     # save the fields for construction later
    #     custom_indicator = CustomIndicatorObject()
    #     custom_indicator.set_api_entity(api_entity)
    #     custom_indicator.set_api_branch(api_branch)
    #     # custom_indicator.set_api_uri(api_uri)
    #     custom_indicator.set_name(name)
    #     custom_dict = OrderedDict()
    #     custom_dict[field1] = None
    #     if field2 is not None:
    #         custom_dict[field2] = None
    #     if field3 is not None:
    #         custom_dict[field3] = None
    #     custom_indicator.set_custom_fields(custom_dict)
    #
    #     # todo include POST to api

    def add(self, indicator, owner=None, type=None, api_entity=None):
        """ add indicator to resource container """
        if type is not None:
            if isinstance(type, IndicatorType):
                if type == IndicatorType.CUSTOM_INDICATORS and not isinstance(indicator, OrderedDict):
                    # change dicts to be Ordered before calling set_indicator
                    field_names = self.tc.indicator_parser.get_field_labels_by_api_entity(api_entity)
                    ordered_indicator = OrderedDict()
                    for field_name in field_names:
                        ordered_indicator[field_name] = indicator.get(field_name)

                    indicator = ordered_indicator

                # generate unique temporary id
                resource_id = uuid.uuid4().int

                # resource object
                resource_obj = self.tc.indicator_parser.construct_typed_indicator(ResourceType(type.value), api_entity=api_entity)
                resource_obj.set_id(int(resource_id))  # set temporary resource id
                resource_obj.set_indicator(indicator, ResourceType(type.value), False)
                resource_obj.set_owner_name(owner)
                resource_obj.set_phase(1)  # set resource api phase (1 = add)

                return self._method_wrapper(resource_obj)

            else:
                raise AttributeError(ErrorCodes.e10060.name.format(indicator))

        elif SharedMethods.validate_indicator(self.tc._indicators_regex, indicator):
            # validate indicator

            # generate unique temporary id
            resource_id = uuid.uuid4().int

            resource_type = get_resource_type(self.tc._indicators_regex, indicator)

            # resource object
            resource_obj = self.tc.indicator_parser.construct_typed_indicator(resource_type)
            resource_obj.set_id(int(resource_id))  # set temporary resource id
            resource_obj.set_indicator(indicator, resource_type, False)
            resource_obj.set_owner_name(owner)
            resource_obj.set_phase(1)  # set resource api phase (1 = add)

            # return object for modification
            return self._method_wrapper(resource_obj)
        else:
            raise AttributeError(ErrorCodes.e10050.name.format(indicator))

    def update(self, indicator, owner=None):
        """ add indicator to resource container """
        # resource object
        resource_type = get_resource_type(self.tc._indicators_regex, indicator)
        resource_obj = self.tc.indicator_parser.construct_typed_indicator(resource_type)
        resource_obj.set_indicator(indicator, resource_type=resource_type, update=True)  # set temporary resource id
        resource_obj.set_owner_name(owner)
        resource_obj.set_phase(2)  # set resource api phase (1 = add)

        # return object for modification
        return self._method_wrapper(resource_obj)

    def delete(self, indicator, owner=None):
        """ add indicator to resource container """
        # generate unique temporary id
        resource_id = indicator

        # resource object
        resource_type = get_resource_type(self.tc._indicators_regex, indicator)
        resource_obj = self.tc.indicator_parser.construct_typed_indicator(resource_type)
        resource_obj.set_id(int(resource_id))  # set temporary resource id
        resource_obj.set_owner_name(owner)
        resource_obj.set_phase(2)  # set resource api phase (1 = add)

        # call delete to queue call
        wrapper = self._method_wrapper(resource_obj)
        wrapper.delete()
        # return object for modification
        return wrapper

    def add_filter(self, resource_type=None, api_entity=None):
        """ add filter to resource container specific to indicator """
        filter_obj = self._filter_class(self.tc,
                                        indicator_type_enum=resource_type,
                                        modified_since=self._modified_since,
                                        api_entity=api_entity)


        # append filter object
        self._filter_objects.append(filter_obj)

        return filter_obj

    @property
    def default_request_object(self):
        """ default request when no filters are provided """
        resource_properties = ApiProperties.api_properties[self._resource_type.name]['properties']
        # create default request object for non-filtered requests
        request_object = RequestObject()
        request_object.set_http_method(resource_properties['base']['http_method'])
        request_object.set_owner_allowed(resource_properties['base']['owner_allowed'])
        request_object.set_request_uri(resource_properties['base']['uri'])
        request_object.set_resource_pagination(resource_properties['base']['pagination'])
        request_object.set_resource_type(self._resource_type)

        # modified since is only support on base (/v2/indicator) api call
        if self._modified_since is not None:
            request_object.set_modified_since(self._modified_since)
            request_object.set_description('Owner Filter modified since {0}'.format(self._modified_since))

        return request_object

    @property
    def indicators(self):
        """ return indicator value """
        for obj in self._objects:
            yield obj.indicator

    @property
    def indicators_list(self):
        """ return list of indicators """
        indicators = []
        for obj in self._objects:
            indicators.append(obj.indicator)
        return indicators

    def set_modified_since(self, data):
        """ set modified time for api query string """
        self._modified_since = data


class IndicatorFilterObject(FilterObject):
    """ """
    def __init__(self, tc_obj, indicator_type_enum=None, modified_since=None, api_entity=None):
        """ init filter object containing api and post filter methods """
        super(IndicatorFilterObject, self).__init__(tc_obj)
        self._owners = []
        self._modified_since = modified_since
        self._api_entity = api_entity

        self.add_resource_properties(indicator_type_enum)
        self.add_filter_methods()

    def add_resource_properties(self, indicator_type_enum):
        # get resource type from indicator type
        if isinstance(indicator_type_enum, IndicatorType):
            if indicator_type_enum is IndicatorType.CUSTOM_INDICATORS:
                self._resource_type = ResourceType.CUSTOM_INDICATORS

                custom_indicator_type = self.tc.indicator_parser.get_custom_indicator_type_by_api_entity(self.api_entity)
                if custom_indicator_type is None:
                    raise AttributeError("api_entity supplied to add_filter method is invalid; " +
                                         "no custom type exists with this api_entity")

                api_branch = custom_indicator_type.api_branch
                self._resource_properties = ApiProperties.get_custom_indicator_properties(self._api_entity, api_branch)['properties']
            # get resource type from indicator type number
            else:
                self._resource_type = ResourceType(indicator_type_enum.value)
                self._resource_properties = ApiProperties.api_properties[self._resource_type.name]['properties']

        else:
            self._resource_type = ResourceType.INDICATORS
            self._resource_properties = ApiProperties.api_properties[self._resource_type.name]['properties']

    def add_filter_methods(self):
        #
        # add_obj filter methods
        #
        for method_name in self._resource_properties.get('filters'):
            if re.findall('add_pf_', method_name):
                self.add_post_filter_names(method_name)
            else:
                self.add_api_filter_name(method_name)
            method = getattr(IndicatorFilterMethods, method_name)
            setattr(self, method_name, types.MethodType(method, self))

    @property
    def api_entity(self):
        return self._api_entity

    @property
    def default_request_object(self):
        """ default request when only a owner filter is provided """
        request_object = RequestObject()
        request_object.set_description('filter by owner')
        request_object.set_http_method(self._resource_properties['base']['http_method'])
        request_object.set_owner_allowed(self._resource_properties['base']['owner_allowed'])
        request_object.set_request_uri(self._resource_properties['base']['uri'])
        request_object.set_resource_pagination(self._resource_properties['base']['pagination'])
        request_object.set_resource_type(self._resource_type)

        # modified since is only support on base (/v2/indicator) api call
        if self._modified_since is not None:
            request_object.set_modified_since(self._modified_since)
            request_object.set_description('Indicator Owner Filter modified since {0}'.format(self._modified_since))

        return request_object
