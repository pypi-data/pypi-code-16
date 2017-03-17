#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
from netbluemind.python import serder

class AuthUser :
	def __init__( self):
		self.uid = None
		self.domainUid = None
		self.displayName = None
		self.value = None
		self.roles = None
		pass

class __AuthUserSerDer__:
	def __init__( self ):
		pass

	def parse(self, value):
		if(value == None):
			return None
		instance = AuthUser()

		self.parseInternal(value, instance)
		return instance

	def parseInternal(self, value, instance):
		uidValue = value['uid']
		instance.uid = serder.STRING.parse(uidValue)
		domainUidValue = value['domainUid']
		instance.domainUid = serder.STRING.parse(domainUidValue)
		displayNameValue = value['displayName']
		instance.displayName = serder.STRING.parse(displayNameValue)
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		valueValue = value['value']
		instance.value = __UserSerDer__().parse(valueValue)
		rolesValue = value['roles']
		instance.roles = serder.SetSerDer(serder.STRING).parse(rolesValue)
		return instance

	def encode(self, value):
		if(value == None):
			return None
		instance = dict()
		self.encodeInternal(value,instance)
		return instance

	def encodeInternal(self, value, instance):

		uidValue = value.uid
		instance["uid"] = serder.STRING.encode(uidValue)
		domainUidValue = value.domainUid
		instance["domainUid"] = serder.STRING.encode(domainUidValue)
		displayNameValue = value.displayName
		instance["displayName"] = serder.STRING.encode(displayNameValue)
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		valueValue = value.value
		instance["value"] = __UserSerDer__().encode(valueValue)
		rolesValue = value.roles
		instance["roles"] = serder.SetSerDer(serder.STRING).encode(rolesValue)
		return instance

