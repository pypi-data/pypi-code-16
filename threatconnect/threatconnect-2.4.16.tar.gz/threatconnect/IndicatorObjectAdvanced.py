import csv
import json
from StringIO import StringIO

import ApiProperties
from AttributeObject import parse_attribute, AttributeObject
from Config.ResourceType import ResourceType
from ErrorCodes import ErrorCodes
from FileOccurrenceObject import parse_file_occurrence
from GroupObject import parse_group
from IndicatorObjectTyped import (AddressIndicatorObject,
                                  CustomIndicatorObject,
                                  EmailAddressIndicatorObject,
                                  FileIndicatorObject,
                                  HostIndicatorObject,
                                  UrlIndicatorObject,)
from ObservationObject import parse_observation
from RequestObject import RequestObject
from SecurityLabelObject import parse_security_label
from SharedMethods import uni, urlsafe
from TagObject import parse_tag
from VictimObject import parse_victim


class IndicatorObjectAdvanced(AddressIndicatorObject,
                              CustomIndicatorObject,
                              EmailAddressIndicatorObject,
                              FileIndicatorObject,
                              HostIndicatorObject,
                              UrlIndicatorObject):

    def __init__(self, tc_obj, resource_container, resource_obj, api_entity=None):
        """ add methods to resource object """
        cls = {
            ResourceType.ADDRESSES: AddressIndicatorObject,
            ResourceType.CUSTOM_INDICATORS: CustomIndicatorObject,
            ResourceType.EMAIL_ADDRESSES: EmailAddressIndicatorObject,
            ResourceType.FILES: FileIndicatorObject,
            ResourceType.HOSTS: HostIndicatorObject,
            ResourceType.URLS: UrlIndicatorObject
        }.get(resource_obj.resource_type)
        super(cls, self).__init__()
        self._resource_container = None
        self._resource_obj = None
        self._resource_properties = None
        self._basic_structure = None
        self._structure = None
        self._tc = None

        if tc_obj is not None and resource_obj is not None and resource_container is not None:
            if resource_obj.resource_type == ResourceType.CUSTOM_INDICATORS:
                custom_indicator_type = tc_obj.indicator_parser.get_custom_indicator_type_by_api_entity(api_entity)
                if custom_indicator_type is None and resource_obj.type is not None:
                    custom_indicator_type = tc_obj.indicator_parser.get_custom_indicator_type_by_name(resource_obj.type)

                if custom_indicator_type is None:
                    raise AttributeError(ErrorCodes.e010020.value(api_entity))

                api_branch = custom_indicator_type.api_branch
                api_entity = custom_indicator_type.api_entity
                self.set_api_branch(api_branch)
                self.set_api_entity(api_entity)
                self._resource_properties = ApiProperties.get_custom_indicator_properties(api_entity, api_branch).get('properties')
            else:
                self._resource_properties = ApiProperties.api_properties.get(resource_obj.resource_type.name).get('properties')

            self._resource_container = resource_container
            self._resource_obj = resource_obj
            self._basic_structure = {
                'confidence': 'confidence',
                'dateAdded': 'date_added',
                'description': 'description',
                'id': 'id',
                'indicator': 'indicator',
                'lastModified': 'last_modified',
                'ownerName': 'owner_name',
                'rating': 'rating',
                'type': 'type',
                'weblink': 'weblink',
            }
            self._structure = self._basic_structure.copy()
            del self._structure['indicator']  # clear up generic indicator name
            self._tc = tc_obj

            # load data from resource_obj
            self.copy_slots(resource_obj)

        #
        # indicator structure
        #
        if self._resource_type == ResourceType.ADDRESSES:
            self._structure['ip'] = 'indicator'
        elif self._resource_type == ResourceType.EMAIL_ADDRESSES:
            self._structure['address'] = 'indicator'
        elif self._resource_type == ResourceType.FILES:
            self._structure['md5'] = 'indicator'
            self._structure['sha1'] = 'indicator'
            self._structure['sha256'] = 'indicator'
            self._structure['size'] = 'size'
        elif self._resource_type == ResourceType.HOSTS:
            self._structure['dnsActive'] = 'dns_active'
            self._structure['hostName'] = 'indicator'
            self._structure['whoisActive'] = 'whois_active'
        elif self._resource_type == ResourceType.URLS:
            self._structure['source'] = 'source'
            self._structure['text'] = 'indicator'
        elif self._resource_type == ResourceType.CUSTOM_INDICATORS:
            self._structure['custom_fields'] = 'indicator'

    def _create_basic_request_object(self, prop_type, *extra_uri_params):
        """
        Creates a RequestObject and populates it based on prop_type.
        extra_uri_params are anything other than self._reference_indicator
        that are needed to create the uri endpoint string,
        thus they must be in the correct order. See ApiProperties.py
        """
        ro = RequestObject()
        if self.resource_type == ResourceType.CUSTOM_INDICATORS:
            all_prop = ApiProperties.get_custom_indicator_properties(api_entity=self.api_entity, api_branch=self.api_branch)
            prop = all_prop.get('properties').get(prop_type)
        else:
            prop = self._resource_properties[prop_type]
        ro.set_request_uri(prop['uri'].format(self._reference_indicator, *extra_uri_params))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        return ro

    def add_attribute(self, attr_type, attr_value, attr_displayed='true'):
        """ add an attribute to an indicator """
        attr_type = uni(attr_type)
        attr_value = uni(attr_value)

        ro = self._create_basic_request_object('attribute_add')

        ro.set_body(json.dumps({
            'type': attr_type,
            'value': attr_value,
            'displayed': attr_displayed}))
        try:
            ro.set_description('add attribute type "{0}" with value "{1}" to {2}'.format(
                attr_type,
                attr_value.encode('ascii', 'ignore'),
                self._reference_indicator.encode('utf-8', 'ignore')))
        except:
            ro.set_description('add attribute type "{0}" with value "unencodable" to {1}'.format(
                attr_type,
                self._reference_indicator.encode('utf-8', 'ignore')))

        callback = lambda status: self.__add_attribute_failure(attr_type, attr_value)
        ro.set_failure_callback(callback)
        self._resource_container.add_commit_queue(self.id, ro)
        attribute = AttributeObject(self)
        attribute.set_type(attr_type)
        attribute.set_value(attr_value)
        attribute.set_displayed(attr_displayed)
        self._resource_obj.add_attribute(attribute)

    def __add_attribute_failure(self, attr_type, attr_value):
        for attribute in self._attributes:
            if attribute.type == attr_type and attribute.value == attr_value:
                self._attributes.remove(attribute)
                break

    def add_false_positive(self):
        """ mark an indicator as a false positive"""
        ro = self._create_basic_request_object('false_positive_add')

        ro.set_description('Adding false positive to {}'.format(self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    def add_file_occurrence(self, fo_file_name=None, fo_path=None, fo_date=None):
        """ add an file occurrence to an indicator """
        if self._resource_type != ResourceType.FILES:
            raise AttributeError(ErrorCodes.e10150.value)

        ro = self._create_basic_request_object('file_occurrence_add')

        json_dict = {}
        if fo_file_name is not None:
            json_dict['fileName'] = fo_file_name
            ro.set_description('add file occurrence - file "{0}" to "{1}"'
                               .format(fo_file_name.encode('ascii', 'ignore'), self._reference_indicator))
        else:
            ro.set_description('add file occurrence - unnamed file to "{0}"'.format(self._reference_indicator))

        if fo_path is not None:
            json_dict['path'] = fo_path
        if fo_date is not None:
            json_dict['date'] = fo_date
        ro.set_body(json.dumps(json_dict))

        self._resource_container.add_commit_queue(self.id, ro)

    def add_observation(self, count, date_observed=None):
        ro = self._create_basic_request_object('observations_add')

        body = {'count': count}
        if date_observed:
            body['dateObserved'] = date_observed

        ro.set_body(json.dumps(body))
        ro.set_description('add observation to {}'.format(self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    def add_tag(self, tag):
        """ add a tag to an indicator """
        ro = self._create_basic_request_object('tag_add', urlsafe(tag))

        ro.set_description('add tag "{0}" to {1}'.format(tag, self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    def associate_group(self, resource_type, resource_id, api_entity=None):
        """ associate a group to indicator by id """
        if resource_type is ResourceType.CUSTOM_INDICATORS:
            api_branch = self._tc.indicator_parser.get_custom_indicator_type_by_api_entity(api_entity).api_branch
            group_uri_attribute = ApiProperties.get_custom_indicator_properties(api_entity, api_branch).get('uri_attribute')
        else:
            group_uri_attribute = ApiProperties.api_properties[resource_type.name]['uri_attribute']
        ro = self._create_basic_request_object(
            'association_group_add', group_uri_attribute, resource_id)

        ro.set_description('associate group type "{0}" id {1} to {2}'.format(
            resource_type.name, resource_id, self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    @property
    def gen_body(self):
        """ generate json body for POST and PUT API requests """
        body_dict = {}
        for prop, values in self._properties.items():
            if getattr(self, prop) is not None:
                # handle custom indicators
                if prop == '_custom_fields':
                    body_dict.update(getattr(self, prop))
                else:
                    body_dict[values['api_field']] = getattr(self, prop)
        return json.dumps(body_dict)

    @property
    def cef(self):
        """ return indicator in CEF format """

        # Version - integer
        cef_version = '0'

        # Vendor - string
        cef_device_vendor = 'threatconnect'

        # Product - string
        cef_device_product = 'threatconnect'

        # Product Version - integer
        cef_product_version = 2

        # CEF Signature (id) - string (in this case id is integer)
        cef_signature_id = self.id

        # Severity - integer
        # The value should be integer 1-10 with 10 be highest.
        # If threatconnect only goes up to 5 some modifications might be a good idea.
        # This could be an algorithm between rating and confidence
        if self.rating is not None:
            cef_severity = (self.rating * 2)
        else:
            cef_severity = 0

        # CEF Name (description) - string
        if self.description is not None:
            cef_name = self.description
        else:
            cef_name = "null"

        #
        # CEF Extension
        #
        cef_extension = ""

        for k, v in sorted(self._structure.items()):
            # handle file indicators
            if k == 'md5':
                cef_extension += '{0}="{1}" '.format(k, getattr(self, v)['md5'])
            elif k == 'sha1':
                cef_extension += '{0}="{1}" '.format(k, getattr(self, v)['sha1'])
            elif k == 'sha256':
                cef_extension += '{0}="{1}" '.format(k, getattr(self, v)['sha256'])
            elif k == 'description':
                continue  # used above
            elif k == 'id':
                continue  # used above
            elif k == 'rating':
                continue  # used above
            elif k == 'custom_fields':
                for label, value in getattr(self, v).items():
                    cef_extension += '{0}="{1}" '.format(label, value)
            else:
                cef_extension += '{0}="{1}" '.format(k, self.cef_format_extension(getattr(self, v)))

        # Build CEF String
        return "CEF:{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}".format(
            cef_version, cef_device_vendor, cef_device_product, cef_product_version,
            cef_signature_id, cef_name, cef_severity, cef_extension)

    # @staticmethod
    # def cef_format_prefix(data):
    #     formatted = data.replace('|', '\|').replace('"\"', '\\')
    #     return formatted

    @staticmethod
    def cef_format_extension(data):
        if data is None or isinstance(data, (int, float)):
            return data
        else:
            formatted = data.replace('"\"', '\\').replace('=', '\=')
        return formatted

    def commit(self):
        """ commit indicator and related associations, attributes, security labels and tags """
        r_id = self.id
        ro = RequestObject()
        ro.set_body(self.gen_body)
        if self.owner_name is not None:
            ro.set_owner(self.owner_name)
        ro.set_resource_type(self.resource_type)
        if self.phase == 1:
            prop = self._resource_properties['add']
            ro.set_description('adding indicator {0}.'.format(self._reference_indicator))
            ro.set_http_method(prop['http_method'])
            ro.set_owner_allowed(prop['owner_allowed'])
            ro.set_request_uri(prop['uri'].format(self._reference_indicator))
            ro.set_resource_pagination(prop['pagination'])
            # validate all required fields are present
            if self.validate:
                api_response = self._tc.api_request(ro)
                if api_response.headers['content-type'] == 'application/json':
                    api_response_dict = api_response.json()
                    if api_response_dict['status'] == 'Success':
                        if self.api_branch is not None and self.api_entity is not None:
                            resource_key = ApiProperties.get_custom_indicator_properties(self.api_entity, self.api_branch).get('resource_key')
                        else:
                            resource_key = ApiProperties.api_properties[self.resource_type.name]['resource_key']
                        r_id = api_response_dict['data'][resource_key]['id']
            else:
                self._tc.tcl.debug('Resource Object'.format(self))
                raise AttributeError(ErrorCodes.e10040.value)
        elif self.phase == 2:
            prop = self._resource_properties['update']
            ro.set_description('update indicator {0}.'.format(self._reference_indicator))
            ro.set_http_method(prop['http_method'])
            ro.set_owner_allowed(prop['owner_allowed'])
            ro.set_request_uri(prop['uri'].format(self._reference_indicator))
            ro.set_resource_pagination(prop['pagination'])
            api_response = self._tc.api_request(ro)
            if api_response.headers['content-type'] == 'application/json':
                api_response_dict = api_response.json()
                if api_response_dict['status'] != 'Success':
                    self._tc.tcl.error('API Request Failure: [{0}]'.format(ro.description))

        # submit all attributes, tags or associations
        for ro in self._resource_container.commit_queue(self.id):
            if self.owner_name is not None:
                ro.set_owner(self.owner_name)
            # replace the id
            if self.phase == 1 and self.id != r_id:
                request_uri = str(ro.request_uri.replace(str(self.id), str(r_id)))
                ro.set_request_uri(request_uri)
            api_response2 = self._tc.api_request(ro)
            if api_response2.headers['content-type'] == 'application/json':
                api_response_dict2 = api_response2.json()
                if api_response_dict2['status'] != 'Success':
                    self._tc.tcl.error('API Request Failure: [{0}]'.format(ro.description))

        if r_id is not None:
            self.set_id(r_id)

        self._resource_container.clear_commit_queue_id(self.id)

        self.set_phase(0)

        if self._reload_attributes:
            self.load_attributes(automatically_reload=True)

        # return object
        return self

    @property
    def csv(self):
        """ return the object in json format """

        indicator = None
        csv_dict = {'indicator': None}
        for k, v in self._basic_structure.items():
            # skip indicator and handle outside of loop
            if k == 'indicator':
                indicator = getattr(self, v)
                continue
            csv_dict[k] = getattr(self, v)

        outfile = StringIO()
        writer = csv.DictWriter(outfile, quotechar='"', fieldnames=sorted(csv_dict.keys()))

        if isinstance(indicator, dict):
            for k, v in indicator.items():
                if v is not None:
                    csv_dict['indicator'] = v
                    writer.writerow(csv_dict)
        else:
            csv_dict['indicator'] = indicator
            writer.writerow(csv_dict)

        return outfile.getvalue().rstrip()

    @property
    def csv_header(self):
        """ return the object in json format """

        csv_dict = {}
        for k, v in self._basic_structure.items():
            csv_dict[k] = v

        outfile = StringIO()
        # not supported in python 2.6
        # writer = csv.DictWriter(outfile, fieldnames=sorted(csv_dict.keys()))
        # writer.writeheader()

        csv_header = ','.join(sorted(csv_dict.keys()))
        outfile.write(csv_header)

        return outfile.getvalue().rstrip()

    def delete(self):
        """ delete indicator """
        ro = self._create_basic_request_object('delete')
        ro.set_description('delete indicator {0}.'.format(self._reference_indicator))

        if self.owner_name is not None:
            ro.set_owner(self.owner_name)

        self._tc.api_request(ro)
        self.set_phase(3)

    def delete_attribute(self, attr_id):
        """ delete attribute from indicator by id """
        ro = self._create_basic_request_object('attribute_delete', attr_id)

        ro.set_description('delete attribute id {0} from {1}'.format(attr_id, self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    def delete_file_occurrence(self, fo_id):
        """ delete file occurrence from indicator by id """
        ro = self._create_basic_request_object('file_occurrence_delete', fo_id)

        ro.set_description('delete file occurrence id {0} from {1}'.format(fo_id, self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    def delete_security_label(self, label):
        """ set the security label for this indicator """
        ro = self._create_basic_request_object('security_label_delete', urlsafe(label))

        ro.set_description('delete security label "{0}" from {1}'.format(label, self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    def delete_tag(self, tag):
        """ delete tag from indicator """
        ro = self._create_basic_request_object('tag_delete', urlsafe(tag))

        ro.set_description('delete tag "{0}" from {1}'.format(tag, self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    def disassociate_group(self, resource_type, resource_id):
        """ disassociate group from indicator """
        group_uri_attribute = ApiProperties.api_properties[resource_type.name]['uri_attribute']
        ro = self._create_basic_request_object(
            'association_group_delete', group_uri_attribute, resource_id)

        ro.set_description('disassociate group type {0} id {1} from {2}'.format(
            resource_type.name, resource_id, self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    @property
    def observations(self):
        """ retrieve observations for this indicator; observations are not stored within the object"""
        ro = self._create_basic_request_object('observations_get')

        ro.set_owner(self.owner_name)
        ro.set_description('retrieve observations for {}'.format(self._reference_indicator))

        for item in self._tc.result_pagination(ro, 'observation'):
            yield parse_observation(item)


    @property
    def group_associations(self):
        """ retrieve associations for this indicator. associations are not stored within the object """
        ro = self._create_basic_request_object('association_groups')

        ro.set_owner(self.owner_name)
        ro.set_description('retrieve group associations for {0}'.format(self._reference_indicator))

        for item in self._tc.result_pagination(ro, 'group'):
            yield parse_group(item, api_filter=ro.description, request_uri=ro.request_uri)

    @property
    def indicator(self):
        if self._resource_type == ResourceType.ADDRESSES:
            return self._ip
        elif self._resource_type == ResourceType.EMAIL_ADDRESSES:
            return self._address
        elif self._resource_type == ResourceType.FILES:
            return {
                'md5': self._md5,
                'sha1': self._sha1,
                'sha256': self._sha256,
            }
        elif self._resource_type == ResourceType.HOSTS:
            return self._hostname
        elif self._resource_type == ResourceType.URLS:
            return self._text
        elif self._resource_type == ResourceType.CUSTOM_INDICATORS:
            return self._custom_fields
        else:
            raise AttributeError(ErrorCodes.e10030.value)

    @property
    def indicator_associations(self):
        """ retrieve associations for this indicator. associations are not stored within the object """
        ro = self._create_basic_request_object('association_indicators')

        ro.set_owner(self.owner_name)
        ro.set_description('retrieve indicator associations for {0}'.format(self._reference_indicator))

        from IndicatorObjectParser import parse_typed_indicator

        for item in self._tc.result_pagination(ro, 'indicator'):
            yield parse_typed_indicator(item,
                                        api_filter=ro.description,
                                        request_uri=ro.request_uri,
                                        indicators_regex=self._tc._indicators_regex,
                                        resource_obj=self._resource_container,
                                        indicator_parser=self._tc.indicator_parser)

    @property
    def json(self):
        """ return the object in json format """
        json_dict = {}
        # handle custom indicators
        if self.custom_fields is not None:
            json_dict.update(self.custom_fields)
        for k, v in self._structure.items():
            # handle file indicators
            if k == 'md5':
                json_dict[k] = getattr(self, v)['md5']
            elif k == 'sha1':
                json_dict[k] = getattr(self, v)['sha1']
            elif k == 'sha256':
                json_dict[k] = getattr(self, v)['sha256']
            else:
                json_dict[k] = getattr(self, v)

        return json_dict


    @property
    def keyval(self):
        """ return the object in json format """
        keyval_str = ''

        # handle custom indicators
        if self.custom_fields is not None:
            for field in self.custom_fields:
                keyval_str += '{0}="{1}" '.format(field, self.custom_fields[field])

        for k, v in sorted(self._structure.items()):
            # handle file indicators
            if k == 'md5':
                keyval_str += '{0}="{1}" '.format(k, getattr(self, v)['md5'])
            elif k == 'sha1':
                keyval_str += '{0}="{1}" '.format(k, getattr(self, v)['sha1'])
            elif k == 'sha256':
                keyval_str += '{0}="{1}" '.format(k, getattr(self, v)['sha256'])
            else:
                keyval_str += '{0}="{1}" '.format(k, getattr(self, v))

        return keyval_str

    @property
    def leef(self):
        """ return indicator in LEEF format """

        """
        https://www-01.ibm.com/support/knowledgecenter/SSMPHH_9.1.0/com.ibm.guardium91.doc/
            appendices/topics/leef_mapping.html

        example:
        Jan 18 11:07:53 host LEEF:Version|Vendor|Product|Version|EventID|
        Key1=Value1<tab>Key2=Value2<tab>Key3=Value3<tab>...<tab>KeyN=ValueN

        Jan 18 11:07:53 192.168.1.1 LEEF:1.0|QRadar|QRM|1.0|NEW_PORT_DISCOVERD|
        src=172.5.6.67 dst=172.50.123.1 sev=5 cat=anomaly msg=there are spaces in this message
        """

        # Version - integer
        leef_version = '0'

        # Vendor - string
        leef_device_vendor = 'threatconnect'

        # Product - string
        leef_device_product = 'threatconnect'

        # Product Version - integer
        leef_product_version = 2

        # LEEF Signature (id) - string (in this case id is integer)
        leef_event_id = self.id

        #
        # LEEF Extension
        #
        leef_extension = ""

        # handle custom indicators
        if self.custom_fields is not None:
            for field in self.custom_fields:
                leef_extension += '{0}="{1}" '.format(field, self.custom_fields[field])

        for k, v in sorted(self._structure.items()):
            # handle file indicators
            if k == 'md5':
                leef_extension += '{0}="{1}" '.format(k, getattr(self, v)['md5'])
            elif k == 'sha1':
                leef_extension += '{0}="{1}" '.format(k, getattr(self, v)['sha1'])
            elif k == 'sha256':
                leef_extension += '{0}="{1}" '.format(k, getattr(self, v)['sha256'])
            elif k == 'dateAdded':
                leef_extension += '{0}="{1}" '.format('devTime', getattr(self, v))
            elif k == 'rating':
                leef_extension += '{0}="{1}" '.format('severity', getattr(self, v))
            else:
                leef_extension += '{0}="{1}" '.format(k, getattr(self, v))

        # Build LEEF String
        return "LEEF:{0}|{1}|{2}|{3}|{4}|{5}".format(
            leef_version, leef_device_vendor, leef_device_product,
            leef_product_version, leef_event_id, leef_extension)

    def load_attributes(self, automatically_reload=False):
        self._reload_attributes = automatically_reload
        """ retrieve attributes for this indicator """
        ro = self._create_basic_request_object('attributes')

        ro.set_owner(self.owner_name)
        ro.set_description('load attributes for {0}'.format(self._reference_indicator))
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['attribute']
                self._resource_obj._attributes = []
                for item in data:
                    self._resource_obj.add_attribute(parse_attribute(item, self))  # add to main resource object

    def load_dns_resolutions(self):
        """ retrieve dns resolution for this indicator """
        if self._resource_type != ResourceType.HOSTS:
            raise AttributeError(ErrorCodes.e10110.value)

        # can't use _create_basic_request_object() because resource_type is different here
        prop = self._resource_properties['dns_resolution']
        ro = RequestObject()
        ro.set_description('load dns resolution for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_owner(self.owner_name)
        ro.set_resource_type(ResourceType.DNS_RESOLUTIONS)

        data = self._tc.api_response_handler(self, ro)
        for item in data:
            self._resource_obj.add_dns_resolution(item)  # add to main resource object

    def load_file_occurrence(self):
        """ retrieve file occurrence for this indicator """
        if self._resource_type != ResourceType.FILES:
            raise AttributeError(ErrorCodes.e10120.value)

        ro = self._create_basic_request_object('file_occurrences')

        ro.set_description('load file occurrence for {0}'.format(self._reference_indicator))

        ro.set_owner(self.owner_name)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['fileOccurrence']
                for item in data:
                    self._resource_obj.add_file_occurrence(parse_file_occurrence(item))  # add to main resource object

    def load_observation_count(self):
        """ retrieve most recent observation count for indicator;
            note this is not the same as observations and will be stored on the indicator """
        ro = self._create_basic_request_object('observation_count_get')

        ro.set_description('load observation count for {}'.format(self._reference_indicator))

        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                # return count for now
                data = api_response_dict['data']['observationCount']['count']
                self.set_observation_count(data)
                if 'lastObserved' in api_response_dict['data']['observationCount']:
                    self.set_last_observed(api_response_dict['data']['observationCount']['lastObserved'])

    def load_security_label(self):
        """ retrieve security label for this indicator """
        ro = self._create_basic_request_object('security_label_load')

        ro.set_description('load security labels for {0}'.format(self._reference_indicator))
        ro.set_owner(self.owner_name)

        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['securityLabel']
                for item in data:
                    self._security_label = parse_security_label(item)  # add to main resource object

    def load_tags(self):
        """ retrieve tags for this indicator """
        ro = self._create_basic_request_object('tags_load')

        ro.set_description('load tags for {0}'.format(self._reference_indicator))
        ro.set_owner(self.owner_name)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['tag']
                for item in data:
                    self._resource_obj.add_tag(parse_tag(item))  # add to main resource object

    def set_security_label(self, label):
        self.add_security_label(label)

    def add_security_label(self, label):
        """ set the security label for this indicator """
        ro = self._create_basic_request_object('security_label_add', urlsafe(label))

        ro.set_description('add security label "{0}" to {1}'.format(label, self._reference_indicator))
        self._resource_container.add_commit_queue(self.id, ro)

    def update_attribute(self, attr_id, attr_value):
        """ update indicator attribute by id """
        ro = self._create_basic_request_object('attribute_update', attr_id)

        attr_value = uni(attr_value)
        ro.set_body(json.dumps({'value': attr_value}))
        try:
            ro.set_description('update attribute id {0} with value "{1}" on {2}'.format(
                attr_id,
                attr_value,
                self._reference_indicator))
        except:
            ro.set_description('update attribute id {0} with value "unencodable" on {1}'.format(
                attr_id,
                self._reference_indicator))

        self._resource_container.add_commit_queue(self.id, ro)

    @property
    def victim_associations(self):
        """ retrieve associations for this indicator. associations are not stored within the object """
        ro = self._create_basic_request_object('association_victims')

        ro.set_owner(self.owner_name)
        ro.set_description('retrieve victim associations for {0}'.format(self._reference_indicator))

        for item in self._tc.result_pagination(ro, 'victim'):
            yield parse_victim(item, api_filter=ro.description, request_uri=ro.request_uri)

    #
    # attributes
    #
    @property
    def attributes(self):
        """ """
        return self._resource_obj._attributes
