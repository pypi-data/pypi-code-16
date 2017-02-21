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
from .user_id import UserId

class Users:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/users"

	def get(self):
		"""Get collection of Account or Sponsor Users"""
		return self.connection.get(self.base_uri)

	def post(self, username, password, first_name, last_name, email, role, **kwargs):
		"""Add a new Account or Sponsor User

		Arguments:
		username -- Username for the user
		password -- User's password
		first_name -- User's first name
		last_name -- User's last name
		email -- User's email
		role -- User's role

		Keyword Arguments:
		mobilePhone -- User's mobile phone number
		phone -- User's main phone number

		"""
		properties = {"userName": username, "password": password, "firstName": first_name, "lastName": last_name, "email": email, "role": role}
		if kwargs is not None:
			properties.update(kwargs)
		return self.connection.post(base_uri, json.dumps(properties))

	def user_id(self, user_id):
		return UserId(self.connection, self.base_uri, user_id)