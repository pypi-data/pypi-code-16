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
from .network import Network
from .sponsor import Sponsor
from .vip_id import VipId

class Vips:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/vips"

	def get(self):
		"""Get a list of VIPs."""
		return self.connection.get(self.base_uri)

	def post(self, network_id, ip_index, name, policy_override_enabled=False):
		"""Create a new VIP.

		Arguments:
		network_id -- The VIP network ID
		ip_index --
		name -- The name of the VIP
		policy_override_enabled -- A boolean determining whether policy override is enabled

		"""
		properties = {"networkId": network_id, "ipIndex": ip_index, "name": name, "policyOverrideEnabled": policy_override_enabled}
		return self.connection.post(self.base_uri, json.dumps(properties))

	def sponsor(self):
		"""Create a Sponsor object."""
		return Sponsor(self.connection, self.base_uri)