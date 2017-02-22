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
from .connection import Connection
from .account_management import AccountManagement
from .provisioning import Provisioning
# from .reporting import Reporting
# from .audit import Audit

class Client:
	def __init__(self, username, password, host="api.security.biz"):
		""" Initialize the client.

		Arguments:
		username -- The username of the user.
		password -- The password of the user.

		Keyword Arguments:
		host -- Allows you to point to a server other than the production server.

		"""
		self.connection = Connection(host)
		self.connection.auth(username, password)

	def provisioning(self):
		"""Create a Provisioning object."""
		return Provisioning(self.connection)

	def account_management(self):
		"""Create an Account Management object."""
		return AccountManagement(self.connection)