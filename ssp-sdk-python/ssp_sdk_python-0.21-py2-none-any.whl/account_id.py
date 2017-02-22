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
from .users import Users

class AccountId:
	def __init__(self, connection, base_uri, account_id):
		self.connection = connection
		self.base_uri = base_uri+"/"+account_id

	def get(self):
		"""Get Account"""
		return self.connection.get(self.base_uri)

	def put(self, account_id, name, status, street, city, state, **kwargs):
		"""Update Account

		Arguments:
		account_id -- The account's unique ID.
		name -- The unique name of the account.
		status -- The account's status.
		street -- The street address for the account.
		city -- The city for the account.
		state -- The state for the account.

		Keyword Arguments:
		zipcode -- The account's zip code.
		country -- The account's country.

		"""
		address = {"street": street, "city": city, "state": state}
		if kwargs is not None:
			address.update(kwargs)
		properties = {"accountId": account_id, "name": name, "status": status, "address": address}
		return self.connection.put(self.base_uri, json.dumps(properties))

	def delete(self):
		"""Delete Account"""
		return self.connection.delete(self.base_uri)

	def head(self):
		"""Head Mapping"""
		return self.connection.head(self.base_uri)

	def users(self):
		"""Create a Users object"""
		return Users(self.connection, self.base_uri)