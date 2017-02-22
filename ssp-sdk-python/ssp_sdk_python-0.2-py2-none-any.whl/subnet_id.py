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

class SubnetId:
	def __init__(self, connection, base_uri, subnet_id):
		self.connection = connection
		self.base_uri = base_uri+"/"+subnet_id

	def get(self):
		"""Fetch a specific Subnet by it's ID."""
		return self.connection.get(self.base_uri)

	def put(self, subnet_id, sponsor_id, vip_id, policy_id, name, cidr, is_suspended=False, **kwargs):
		"""Update a specific Subnet."""
		properties = {"id": subnet_id, "sponsorId": sponsor_id, "accountId": account_id, "vipId": vip_id, "policyId": policy_id, "cidr": cidr, "isSuspended": is_suspended, "name": name}
		if kwargs is not None:
			properties.update(kwargs)
		return self.connection.put(self.base_uri, json.dumps(properties))

	def delete(self):
		"""Delete a specific Subnet."""
		return self.connection.delete(self.base_uri)