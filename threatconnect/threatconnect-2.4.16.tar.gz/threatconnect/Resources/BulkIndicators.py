""" standard """
import re
import types

""" custom """
from threatconnect import IndicatorFilterMethods
from threatconnect import ApiProperties
from threatconnect.Config.ResourceType import ResourceType
from threatconnect.FilterObject import FilterObject
from threatconnect.RequestObject import RequestObject
from threatconnect.Resource import Resource


class BulkIndicators(Resource):
    """ """

    def __init__(self, tc_obj, on_demand=False):
        """ """
        super(BulkIndicators, self).__init__(tc_obj)

        self._filter_class = BulkIndicatorFilterObject
        self._resource_type = ResourceType.INDICATORS
        self._on_demand = on_demand
        if on_demand:
            tc_obj._bulk_on_demand = True

    def _method_wrapper(self, resource_object):
        """ return resource object as new object with additional methods """
        return self.tc.indicator_parser.construct_typed_advanced_indicator(self, resource_object)


    @property
    def default_request_object(self):
        """ default request when no filters are provided """
        resource_properties = ApiProperties.api_properties[self._resource_type.name]['properties']
        # create default request object for non-filtered requests
        request_object = RequestObject()
        request_object.set_http_method(resource_properties['bulk']['http_method'])
        request_object.set_owner_allowed(resource_properties['bulk']['owner_allowed'])
        request_object.set_request_uri(resource_properties['bulk']['uri'])
        request_object.set_resource_pagination(resource_properties['bulk']['pagination'])
        request_object.set_resource_type(self._resource_type)
        if self._on_demand:
            request_object.add_payload('runNow', True)

        return request_object

    def add_filter(self, resource_type=None, api_entity=None):
        """ add filter to resource container specific to indicator """
        filter_obj = self._filter_class(self.tc, api_entity=api_entity)

        # append filter object
        self._filter_objects.append(filter_obj)

        return filter_obj


class BulkIndicatorFilterObject(FilterObject):
    """ """

    def __init__(self, tc_obj, api_entity=None):
        """ """
        super(BulkIndicatorFilterObject, self).__init__(tc_obj)
        self._owners = []
        self._api_entity = api_entity

        self._resource_type = ResourceType.INDICATORS
        self._resource_properties = ApiProperties.api_properties[self._resource_type.name]['properties']

        #
        # add_obj filter methods
        #
        for method_name in self._resource_properties['filters']:
            # only add post filters for Bulk Indicator download
            if re.findall('add_pf_', method_name):
                self.add_post_filter_names(method_name)
                method = getattr(IndicatorFilterMethods, method_name)
                setattr(self, method_name, types.MethodType(method, self))

    @property
    def api_entity(self):
        return self._api_entity

    @ property
    def default_request_object(self):
        """ default request when only a owner filter is provided """
        request_object = RequestObject()
        request_object.set_description('filter by owner')
        request_object.set_http_method(self._resource_properties['bulk']['http_method'])
        request_object.set_owner_allowed(self._resource_properties['bulk']['owner_allowed'])
        request_object.set_request_uri(self._resource_properties['bulk']['uri'])
        request_object.set_resource_pagination(self._resource_properties['bulk']['pagination'])
        request_object.set_resource_type(self._resource_type)
        request_object.set_stream(True)

        if self.tc._bulk_on_demand:
            request_object.add_payload('runNow', True)

        return request_object