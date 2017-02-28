# Copyright (C) 2016 A10 Networks Inc. All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
import unittest

import a10_openstack_lib.resources.a10_certificate as a10_certificate
import a10_openstack_lib.resources.a10_device_instance as a10_device_instance
import a10_openstack_lib.resources.a10_scaling_group as a10_scaling_group
import a10_openstack_lib.resources.template as template


class TestResources(unittest.TestCase):

    def check_resource_attribute_map(self, resources):
        supported_attributes = [
            'convert_to_int',
            'convert_kvp_list_to_dict',
            'convert_to_list',
            'convert_kvp_to_list',
            'ATTR_NOT_SPECIFIED'
        ]
        mock_attributes = mock.Mock(spec=supported_attributes)

        # This shouldn't blow up:
        template.apply_template(resources, mock_attributes)

    def test_a10_certificate(self):
        self.check_resource_attribute_map(a10_certificate.RESOURCE_ATTRIBUTE_MAP)

    def test_a10_device_instance(self):
        self.check_resource_attribute_map(a10_device_instance.RESOURCE_ATTRIBUTE_MAP)

    def test_a10_scaling_group(self):
        self.check_resource_attribute_map(a10_scaling_group.RESOURCE_ATTRIBUTE_MAP)
