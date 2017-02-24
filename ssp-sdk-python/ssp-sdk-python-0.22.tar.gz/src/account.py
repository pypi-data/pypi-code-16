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

class Account:
	def __init__(self, connection, base_uri):
		self.connection = connection
		self.base_uri = base_uri+"/account"

	def account_id(self, account_id):
		"""Create an Account Id object"""
		return AccountId(self.connection, self.base_uri, account_id)