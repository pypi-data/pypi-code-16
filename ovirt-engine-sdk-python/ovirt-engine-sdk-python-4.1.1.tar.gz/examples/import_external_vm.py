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

# This example will import a VM from an export domain using a
# target domain, the example assumes there is an exported vm in
# the export storage domain

# Create a connection to the server:
connection = sdk.Connection(
    url='https://engine/ovirt-engine/api',
    username='admin@internal',
    password='123',
    ca_file='ca.pem',
    debug=True,
    log=logging.getLogger(),
)

# Get the reference to the service that manages import of external virtual machines:
imports_service = connection.system_service().external_vm_imports_service()

# Initiate the import of VM 'myvm' from VMware:
imports_service.add(
    import_=types.ExternalVmImport(
        name='vm',
        vm=types.Vm(
            name='vmwarevm',
        ),
        provider=types.ExternalVmProviderType.VMWARE,
        username='administrator',
        password='Heslo123',
        url='vpx://administrator@10.35.5.21/Folder1/Folder2/Compute3/Folder4/Cluster5/10.35.72.10?no_verify=1',
        cluster=types.Cluster(
            name='test-cluster',
        ),
        storage_domain=types.StorageDomain(
            name='nfs',
        ),
        sparse=True,
    )
)

# Close the connection to the server:
connection.close()
