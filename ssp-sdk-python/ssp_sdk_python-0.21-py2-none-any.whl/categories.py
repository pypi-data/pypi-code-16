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
from .category_id import CategoryId

class Categories:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/categories"

	def get(self):
		"""Get a list of Categories."""
		return self.connection.get(self.base_uri)

	def post(self, category_id, name, description, weight, category_ref, sponsor_id):
		"""Create a new Category.

		Arguments:
		category_id -- A unique ID for the category.
		name -- The name of the category.
		description -- A description of the category.
		weight --
		category_ref -- 
		sponsor_id -- The sponsor ID for the category.

		"""
		properties = {"id": category_id, "name": name, "description": description, "weight": weight, "categoryRef": category_ref, "sponsorId": sponsor_id}
		return self.service.post(self.base_uri, json.dumps(properties))

	def category_id(self, category_id):
		"""Create a Category Id object."""
		return CategoryId(self.connection, self.base_uri, category_id)