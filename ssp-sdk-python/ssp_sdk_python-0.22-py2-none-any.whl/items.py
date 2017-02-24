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

class Items:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/items"

	def get(self):
		"""Find items belonging to a specific Blacklist or Whitelist."""
		return self.connection.get(self.base_uri)

	def post(self, records):
		"""Add item(s) to a specific Blacklist.

		Argument:
		records -- A list of hosts to block.

		"""
		properties = {"records": records}
		return self.connection.post(self.base_uri, json.dumps(properties))

	def delete(self):
		"""Delete item(s) from a specific Whitelist."""
		return self.connection.delete(self.base_uri)