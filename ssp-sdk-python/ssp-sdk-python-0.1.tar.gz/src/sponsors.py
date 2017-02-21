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
from .sponsor_id import SponsorId

class Sponsors:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/sponsors"

	def get(self):
		"""Get a collection of Sponsors."""
		return self.connection.get(self.base_uri)

	def post(self, name, street, city, state, **kwargs):
		"""Add a new Sponsor.

		Arguments:
		name -- A unique name for the sponsor.
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
		properties = {"name": name, "address": address}
		return self.connection.post(self.base_uri, json.dumps(properties))

	def sponsor_id(self, sponsor_id):
		"""Create a Sponsor Id object."""
		return SponsorId(self.connection, self.base_uri, sponsor_id)