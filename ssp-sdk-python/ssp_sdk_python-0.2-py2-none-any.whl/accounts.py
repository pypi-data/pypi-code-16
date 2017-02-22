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
from .account_id import AccountId

class Accounts:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/accounts"

	def get(self):
		"""Get collection of Accounts"""
		return self.connection.get(self.base_uri)

	def post(self, name, street, city, state, **kwargs):
		"""Add a new Account

		Arguments:
		name -- The unique name of the account.
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
		properties = {"name": name, "address": address}
		return self.connection.post(self.base_uri, json.dumps(properties))

	def account_id(self, account_id):
		"""Create an Account Id object"""
		return AccountId(self.connection, self.base_uri, account_id)