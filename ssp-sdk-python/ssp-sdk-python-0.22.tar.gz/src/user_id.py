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

class UserId:
	def __init__(self, connection, base_uri, user_id):
		self.connection = connection
		self.base_uri = base_uri+"/"+user_id

	def get(self):
		"""Get Account or Sponsor User"""
		return self.connection.get(self.base_uri)

	def put(self, user_id, username, first_name, last_name, email, role, status, **kwargs):
		"""Update Account User

		Arguments:
		user_id -- User's unique ID
		username -- Username for the user
		password -- User's password
		first_name -- User's first name
		last_name -- User's last name
		email -- User's email
		role -- User's role
		status -- User's status

		Keyword Arguments:
		mobilePhone -- User's mobile phone number
		phone -- User's main phone number
		createdBy -- Sponsor or account that created the user
		createdDate -- Date the user was created
		updatedBy -- Last sponsor or account to update the user
		updatedDate -- Date the user was last updated

		"""
		properties = {"userId": user_id, "userName": username, "firstName": first_name, "lastName": last_name, "email": email, "role": role, "status": status}
		if kwargs is not None:
			properties.update(kwargs)
		return self.connection.put(self.base_uri, json.dumps(properties))

	def delete(self):
		"""Delete Account or Sponsor User"""
		return self.connection.delete(self.base_uri)