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
from .accounts import Accounts
from .users import Users

class SponsorId:
	def __init__(self, connection, base_uri, sponsor_id):
		self.connection = connection
		self.base_uri = base_uri+"/"+sponsor_id

	def get(self):
		"""Get Sponsor"""
		return self.connection.get(self.base_uri)

	def put(self, sponsor_id, name, status, street, city, state, **kwargs):
		"""Update Sponsor

		Arguments:
		sponsor_id -- The sponsor's unique ID.
		name -- The sponsor's unique name.
		status -- The sponsor's status.
		street -- The sponsor's street address.
		city -- The sponsor's city.
		state -- The sponsor's state.

		Keyword Arguments:
		zipcode -- The sponsor's zip code.
		country -- The sponsor's country.

		"""
		address = {"street": street, "city": city, "state": state}
		if kwargs is not None:
			address.update(kwargs)
		properties = {"sponsorId": sponsor_id, "name": name, "status": status, "address": address}
		return self.connection.put(self.base_uri, json.dumps(properties))

	def delete(self):
		"""Delete Sponsor"""
		return self.connection.delete(self.base_uri)

	def accounts(self):
		"""Create an Accounts object"""
		return Accounts(self.connection, self.base_uri)

	def Users(self):
		"""Create a Users object"""
		return Users(self.connection, self.base_uri)