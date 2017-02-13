# Copyright (c) 2016 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.request as request
from qumulo.lib.uri import UriBuilder

@request.request
def start_listener(conninfo, credentials):
    method = "POST"
    uri = UriBuilder(path="/v1/replication/start-listener")
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def stop_listener(conninfo, credentials):
    method = "POST"
    uri = UriBuilder(path="/v1/replication/stop-listener")
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def replicate(conninfo, credentials, relationship):
    method = "POST"
    uri = "/v1/replication/relationships/{}/replicate".format(relationship)
    return request.rest_request(
        conninfo, credentials, method, unicode(uri))

@request.request
def create_relationship(
        conninfo,
        credentials,
        source_dir,
        target_dir,
        address,
        port):

    body = {'source_dir': source_dir,
            'target_dir': target_dir,
            'target_address': address,
            'target_port': port}
    method = "POST"
    uri = "/v1/replication/relationships/"
    return request.rest_request(conninfo, credentials, method, uri, body=body)

@request.request
def list_relationships(conninfo, credentials):
    method = "GET"
    uri = "/v1/replication/relationships/"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_relationship(conninfo, credentials, relationship_id):
    method = "GET"
    uri = "/v1/replication/relationships/{}"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def delete_relationship(conninfo, credentials, relationship_id):

    method = "DELETE"
    uri = "/v1/replication/relationships/{}"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def get_relationship_status(conninfo, credentials, relationship_id):

    method = "GET"
    uri = "/v1/replication/relationships/{}/status"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def authorize_source(conninfo, credentials, relationship_id):

    method = "POST"
    uri = "/v1/replication/relationships/{}/authorize-source"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def authorize_target(conninfo, credentials, relationship_id):

    method = "POST"
    uri = "/v1/replication/relationships/{}/authorize-target"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))
