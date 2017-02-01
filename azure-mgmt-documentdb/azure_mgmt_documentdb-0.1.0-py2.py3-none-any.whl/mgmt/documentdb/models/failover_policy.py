# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class FailoverPolicy(Model):
    """The failover policy for a given region of a database account.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar id: The unique identifier of the region in which the database
     account replicates to. Example: &lt;accountName&gt;-&lt;locationName&gt;.
    :vartype id: str
    :param location_name: The name of the region in which the database account
     exists.
    :type location_name: str
    :param failover_priority: The failover priority of the region. A failover
     priority of 0 indicates a write region. The maximum value for a failover
     priority = (total number of regions - 1). Failover priority values must be
     unique for each of the regions in which the database account exists.
    :type failover_priority: int
    """

    _validation = {
        'id': {'readonly': True},
        'failover_priority': {'minimum': 0},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'location_name': {'key': 'locationName', 'type': 'str'},
        'failover_priority': {'key': 'failoverPriority', 'type': 'int'},
    }

    def __init__(self, location_name=None, failover_priority=None):
        self.id = None
        self.location_name = location_name
        self.failover_priority = failover_priority
