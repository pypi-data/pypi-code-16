# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#


"""
"sourceInfo" : {
     "type" : "com.formationds.events.model.ServiceSource",
     "id" : "1",
     "nodeId" : 1000,
     "nodeAddress" : "mynode.mydomain.com",
     "pid" : 1234,
     "processName" : "java blah blah",
     "serviceId" : 1004,
     "serviceType" : "OM",
     "serviceVersion" : "0.1.0",
     "attributes" : { }
   },
"""

class EventSourceInfo(object):
    """
    Models a SourceInfo structure sent by the Event service to track items such as the node ID, service ID, PID, etc
    of the sender.
    """

    def __init__(self, source_id="", node_id=0, node_address="", pid=0, process_name="", service_id=0,
                 service_type="", service_version="", domain_id=0, domain_name="", attributes=None):

        self._source_id = source_id
        self._node_id = node_id
        self._node_address = node_address
        self._pid = pid
        self._process_name = process_name
        self._service_id = service_id
        self._service_type = service_type
        self._service_version = service_version
        self._domain_id = domain_id
        self._domain_name = domain_name

        if attributes is None:
            self._attributes = {}

    @property
    def source_id(self):
        return self._source_id

    @source_id.setter
    def source_id(self, source_id):
        self._source_id = source_id

    @property
    def node_id(self):
        return self._node_id

    @node_id.setter
    def node_id(self, node_id):
        self._node_id = node_id

    @property
    def node_address(self):
        return self._node_address

    @node_address.setter
    def node_address(self, node_address):
        self._node_address = node_address

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, pid):
        self._pid = pid

    @property
    def process_name(self):
        return self._process_name

    @process_name.setter
    def process_name(self, process_name):
        self._process_name = process_name

    @property
    def service_id(self):
        return self._service_id

    @service_id.setter
    def service_id(self, value):
        self._service_id = value

    @property
    def service_type(self):
        return self._service_type

    @service_type.setter
    def service_type(self, value):
        self._service_type = value

    @property
    def service_version(self):
        return self._service_version

    @service_version.setter
    def service_version(self, value):
        self._service_version = value

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        self._attributes = value

    @property
    def domain_id(self):
        return self._domain_id

    @domain_id.setter
    def domain_id(self, value):
        self._domain_id = value

    @property
    def domain_name(self):
        return self._domain_name

    @domain_name.setter
    def domain_name(self, value):
        self._domain_name = value
