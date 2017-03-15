#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging

import ovirtsdk4 as sdk
import ovirtsdk4.types as types

logging.basicConfig(level=logging.DEBUG, filename='example.log')

# This example will connect to the server, find a virtual machine and enable the
# serial console if it isn't enabled yet:

# Create the connection to the server:
connection = sdk.Connection(
    url='https://ondra.local/ovirt-engine/api',
    username='admin@internal',
    password='123456',
    #ca_file='ca.pem',
    insecure=True,
    debug=True,
    log=logging.getLogger(),
)


# Get the reference to the service that manages import of external virtual machines:
imports_service = connection.system_service().external_vm_imports_service()

# Initiate the import of VM 'myvm' from VMware:
imports_service.add(
    types.ExternalVmImport(
        vm=types.Vm(
            name='mytest'
        ),
        #username='xxxxxxxxx',
        #password='asdas',
        name='rhel7_headless_xen',
        provider=types.ExternalVmProviderType.XEN,
        url='xen+ssh://root@alma02.qa.lab.tlv.redhat.com',
        cluster=types.Cluster(
            name='cl-41',
        ),
        storage_domain=types.StorageDomain(
            name='sd',
        ),
        sparse=True,
    )
)

# Close the connection to the server:
connection.close()