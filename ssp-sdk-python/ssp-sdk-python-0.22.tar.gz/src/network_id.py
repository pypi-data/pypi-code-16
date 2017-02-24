# Copyright 2017 NeuStar, Inc.All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json

class NetworkId:
	def __init__(self, connection, base_uri, network_id):
		self.connection = connection
		self.base_uri = base_uri+"/"+network_id

	def get(self):
		"""Get a specific Network."""
		return self.connection.get(self.base_uri)

	def delete(self):
		"""Delete a Network."""
		return self.connection.delete(self.base_uri)

	def put_name(self, name):
		"""Update the name of a Network."""
		return self.connection.put(self.base_uri+"/name", name)

	def put_sponsor_id(self, sponsor_id):
		"""Assign a Sponsor to a Network."""
		return self.connection.put(self.base_uri+"/sponsorId", sponsor_id)

	def delete_sponsor_id(self, sponsor_id):
		"""Unassign Sponsor from Network."""
		return self.connection.delete(self.base_uri+"/sponsorId")