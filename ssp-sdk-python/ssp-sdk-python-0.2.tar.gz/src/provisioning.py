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
from .networks import Networks
from .vips import Vips
from .subnets import Subnets
from .categories import Categories
from .blacklists import Blacklists
# from .whitelists import Whitelists
# from .policies import Policies
# from .messages import Messages


class Provisioning:
	def __init__(self, connection):
		self.connection = connection
		self.base_uri = "/rdns/provisioning/v1"

	def networks(self):
		"""Create a Network object."""
		return Networks(self.connection, self.base_uri)

	def vips(self):
		return Vips(self.connection, self.base_uri)

	def subnets(self):
		return Subnets(self.connection, self.base_uri)

	def categories(self):
		return Categories(self.connection, self.base_uri)

	def blacklists(self):
		return Blacklists(self.connection, self.base_uri)

	# def whitelists(self):
	# 	return Whitelists(self.connection, self.base_uri)

	# def policies(self):
	# 	return Policies(self.connection, self.base_uri)

	# def messages(self):
	# 	return Messages(self.connection, self.base_uri)
