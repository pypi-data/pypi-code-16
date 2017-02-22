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

class VipId:
	def __init__(self, connection, base_uri, vip_id):
		self.connection = connection
		self.base_uri = base_uri+"/"+vip_id

	def get(self):
		"""Fetch a specific VIP."""
		return self.connection.get(self.base_uri)

	def put(self, vip_id, network_id, sponsor_id, policy_id, name, ip_index, is_suspended=False, policy_override_enabled=False, description=None):
		"""Update a specific VIP pair.

		vip_id -- The VIP's unique ID

		"""
		properties = {"id": vip_id, "networkId": network_id, "sponsorId": sponsor_id, "policyId": policy_id, "name": name, "description": description, "ipIndex": ip_index, "isSuspended": is_suspended, "policyOverrideEnabled": policy_override_enabled}
		return self.connection.put(self.base_uri, json.dumps(properties))

	def delete(self):
		"""Delete a VIP pair."""
		return self.connection.delete(self.base_uri)