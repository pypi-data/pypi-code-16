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
from .items import Items

class BlacklistId:
	def __init__(self, connection, base_uri, blacklist_id):
		self.connection = connection
		self.base_uri = base_uri+"/"+blacklist_id

	def get(self):
		"""Find a specific blacklist."""
		return self.connection.get(self.base_uri)

	def put(self, sponsor_id, account_id, name, description, **kwargs):
		"""Update a specific Blacklist."""
		properties = {"sponsorId": sponsor_id, "accountId": account_id, "name": name, "description": description}
		if kwargs is not None:
			properties.update(kwargs)
		return self.connection.put(self.base_uri, json.dumps(properties))

	def delete(self):
		"""Delete a specific Blacklist."""
		return self.connection.delete(self.base_uri)

	def items(self):
		"""Create an Items object."""
		return Items(self.connection, self.base_uri)