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

class Mailshare :
	def __init__( self):
		self.name = None
		self.archived = None
		self.emails = None
		self.quota = None
		self.routing = None
		self.dataLocation = None
		pass

class __MailshareSerDer__:
	def __init__( self ):
		pass

	def parse(self, value):
		if(value == None):
			return None
		instance = Mailshare()

		self.parseInternal(value, instance)
		return instance

	def parseInternal(self, value, instance):
		nameValue = value['name']
		instance.name = serder.STRING.parse(nameValue)
		archivedValue = value['archived']
		instance.archived = serder.BOOLEAN.parse(archivedValue)
		from netbluemind.core.api.Email import Email
		from netbluemind.core.api.Email import __EmailSerDer__
		emailsValue = value['emails']
		instance.emails = serder.CollectionSerDer(__EmailSerDer__()).parse(emailsValue)
		quotaValue = value['quota']
		instance.quota = serder.INT.parse(quotaValue)
		from netbluemind.mailbox.api.MailboxRouting import MailboxRouting
		from netbluemind.mailbox.api.MailboxRouting import __MailboxRoutingSerDer__
		routingValue = value['routing']
		instance.routing = __MailboxRoutingSerDer__().parse(routingValue)
		dataLocationValue = value['dataLocation']
		instance.dataLocation = serder.STRING.parse(dataLocationValue)
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
		archivedValue = value.archived
		instance["archived"] = serder.BOOLEAN.encode(archivedValue)
		from netbluemind.core.api.Email import Email
		from netbluemind.core.api.Email import __EmailSerDer__
		emailsValue = value.emails
		instance["emails"] = serder.CollectionSerDer(__EmailSerDer__()).encode(emailsValue)
		quotaValue = value.quota
		instance["quota"] = serder.INT.encode(quotaValue)
		from netbluemind.mailbox.api.MailboxRouting import MailboxRouting
		from netbluemind.mailbox.api.MailboxRouting import __MailboxRoutingSerDer__
		routingValue = value.routing
		instance["routing"] = __MailboxRoutingSerDer__().encode(routingValue)
		dataLocationValue = value.dataLocation
		instance["dataLocation"] = serder.STRING.encode(dataLocationValue)
		return instance

