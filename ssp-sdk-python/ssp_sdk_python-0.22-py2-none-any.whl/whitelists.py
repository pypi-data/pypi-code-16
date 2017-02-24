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
from .whitelist_id import WhitelistId
from .sponsor import Sponsor
from .account import Account

class Whitelists:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/whitelists"

	def get(self):
		"""Get a list of whitelists."""
		return self.connection.get(self.base_uri)

	def post(self, account_id, name, **kwargs):
		"""Create a new Whitelist.

		Arguments:
		account_id -- The account ID associated with the whitelist.
		name -- The name of the whitelist.

		Keyword Arguments:
		sponsorId -- The sponsor ID associated with the whitelist (only required for NeustarAdmins)
		description -- A description of the whitelist.

		"""
		properties = {"accountId": account_id, "name": name}
		if kwargs is not None:
			properties.update(kwargs)
		return self.connection.post(self.base_uri, json.dumps(properties))

	def whitelist_id(self, whitelist_id):
		"""Create a Whitelist Id object."""
		return BlacklistId(self.connection, self.base_uri, whitelist_id)

	def sponsor(self):
		"""Create a Sponsor object."""
		return Sponsor(self.connection, self.base_uri)

	def account(self):
		"""Create an Account object."""
		return Account(self.connection, self.base_uri)