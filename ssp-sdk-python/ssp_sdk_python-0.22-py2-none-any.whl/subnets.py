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
from .subnet_id import SubnetId
from .sponsor import Sponsor


class Subnets:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/subnets"

	def get(self):
		"""Fetch a list of Subnets."""
		return self.connection.get(self.base_uri)

	def post(self, sponsor_id, account_id, vip_id, cidr, name, **kwargs):
		"""Create a new Subnet.

		Arguments:
		sponsor_id -- A unique sponsor ID to assign the subnet
		account_id -- A unique account ID to assign the subnet
		vip_id -- A unique VIP ID to assign the subnet
		cidr -- The subnet's classless inter-domain routing number
		name -- The name of the subnet

		Keyword Arguments:
		policyId -- A unique policy ID to assign the subnet
		description -- A description of the subnet

		"""
		properties = {"sponsorId": sponsor_id, "accountId": account_id, "vipId": vip_id, "cidr": cidr, "name": name}
		if kwargs is not None:
			properties.update(kwargs)
		self.connection.post(self.base_uri, json.dumps(properties))

	def subnet_id(self, subnet_id):
		"""Create a Subnet Id object."""
		return SubnetId(self.connection, self.base_uri, subnet_id)

	def sponsor(self):
		"""Create a Sponsor object."""
		return Sponsor(self.connection, self.base_uri)
