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

class Group :
	def __init__( self):
		self.name = None
		self.description = None
		self.properties = None
		self.emails = None
		self.hidden = None
		self.hiddenMembers = None
		self.mailArchived = None
		self.dataLocation = None
		self.memberCount = None
		pass

class __GroupSerDer__:
	def __init__( self ):
		pass

	def parse(self, value):
		if(value == None):
			return None
		instance = Group()

		self.parseInternal(value, instance)
		return instance

	def parseInternal(self, value, instance):
		nameValue = value['name']
		instance.name = serder.STRING.parse(nameValue)
		descriptionValue = value['description']
		instance.description = serder.STRING.parse(descriptionValue)
		propertiesValue = value['properties']
		instance.properties = serder.MapSerDer(serder.STRING).parse(propertiesValue)
		from netbluemind.core.api.Email import Email
		from netbluemind.core.api.Email import __EmailSerDer__
		emailsValue = value['emails']
		instance.emails = serder.CollectionSerDer(__EmailSerDer__()).parse(emailsValue)
		hiddenValue = value['hidden']
		instance.hidden = serder.BOOLEAN.parse(hiddenValue)
		hiddenMembersValue = value['hiddenMembers']
		instance.hiddenMembers = serder.BOOLEAN.parse(hiddenMembersValue)
		mailArchivedValue = value['mailArchived']
		instance.mailArchived = serder.BOOLEAN.parse(mailArchivedValue)
		dataLocationValue = value['dataLocation']
		instance.dataLocation = serder.STRING.parse(dataLocationValue)
		memberCountValue = value['memberCount']
		instance.memberCount = serder.INT.parse(memberCountValue)
		return instance

	def encode(self, value):
		if(value == None):
			return None
		instance = dict()
		self.encodeInternal(value,instance)
		return instance

	def encodeInternal(self, value, instance):

		nameValue = value.name
		instance["name"] = serder.STRING.encode(nameValue)
		descriptionValue = value.description
		instance["description"] = serder.STRING.encode(descriptionValue)
		propertiesValue = value.properties
		instance["properties"] = serder.MapSerDer(serder.STRING).encode(propertiesValue)
		from netbluemind.core.api.Email import Email
		from netbluemind.core.api.Email import __EmailSerDer__
		emailsValue = value.emails
		instance["emails"] = serder.CollectionSerDer(__EmailSerDer__()).encode(emailsValue)
		hiddenValue = value.hidden
		instance["hidden"] = serder.BOOLEAN.encode(hiddenValue)
		hiddenMembersValue = value.hiddenMembers
		instance["hiddenMembers"] = serder.BOOLEAN.encode(hiddenMembersValue)
		mailArchivedValue = value.mailArchived
		instance["mailArchived"] = serder.BOOLEAN.encode(mailArchivedValue)
		dataLocationValue = value.dataLocation
		instance["dataLocation"] = serder.STRING.encode(dataLocationValue)
		memberCountValue = value.memberCount
		instance["memberCount"] = serder.INT.encode(memberCountValue)
		return instance

