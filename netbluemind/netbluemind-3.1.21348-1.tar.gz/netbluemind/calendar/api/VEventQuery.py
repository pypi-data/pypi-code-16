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

class VEventQuery :
	def __init__( self):
		self.query = None
		self.from_ = None
		self.size = None
		self.escapeQuery = None
		self.resolveRecur = None
		self.dateMin = None
		self.dateMax = None
		self.resolveAttendees = None
		self.attendee = None
		self.eventUid = None
		self.recurid = None
		self.anyRecurId = None
		pass

class __VEventQuerySerDer__:
	def __init__( self ):
		pass

	def parse(self, value):
		if(value == None):
			return None
		instance = VEventQuery()

		self.parseInternal(value, instance)
		return instance

	def parseInternal(self, value, instance):
		queryValue = value['query']
		instance.query = serder.STRING.parse(queryValue)
		from_Value = value['from']
		instance.from_ = serder.INT.parse(from_Value)
		sizeValue = value['size']
		instance.size = serder.INT.parse(sizeValue)
		escapeQueryValue = value['escapeQuery']
		instance.escapeQuery = serder.BOOLEAN.parse(escapeQueryValue)
		resolveRecurValue = value['resolveRecur']
		instance.resolveRecur = serder.BOOLEAN.parse(resolveRecurValue)
		from netbluemind.core.api.date.BmDateTime import BmDateTime
		from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
		dateMinValue = value['dateMin']
		instance.dateMin = __BmDateTimeSerDer__().parse(dateMinValue)
		from netbluemind.core.api.date.BmDateTime import BmDateTime
		from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
		dateMaxValue = value['dateMax']
		instance.dateMax = __BmDateTimeSerDer__().parse(dateMaxValue)
		resolveAttendeesValue = value['resolveAttendees']
		instance.resolveAttendees = serder.BOOLEAN.parse(resolveAttendeesValue)
		from netbluemind.calendar.api.VEventAttendeeQuery import VEventAttendeeQuery
		from netbluemind.calendar.api.VEventAttendeeQuery import __VEventAttendeeQuerySerDer__
		attendeeValue = value['attendee']
		instance.attendee = __VEventAttendeeQuerySerDer__().parse(attendeeValue)
		eventUidValue = value['eventUid']
		instance.eventUid = serder.STRING.parse(eventUidValue)
		from netbluemind.core.api.date.BmDateTime import BmDateTime
		from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
		recuridValue = value['recurid']
		instance.recurid = __BmDateTimeSerDer__().parse(recuridValue)
		anyRecurIdValue = value['anyRecurId']
		instance.anyRecurId = serder.BOOLEAN.parse(anyRecurIdValue)
		return instance

	def encode(self, value):
		if(value == None):
			return None
		instance = dict()
		self.encodeInternal(value,instance)
		return instance

	def encodeInternal(self, value, instance):

		queryValue = value.query
		instance["query"] = serder.STRING.encode(queryValue)
		from_Value = value.from_
		instance["from"] = serder.INT.encode(from_Value)
		sizeValue = value.size
		instance["size"] = serder.INT.encode(sizeValue)
		escapeQueryValue = value.escapeQuery
		instance["escapeQuery"] = serder.BOOLEAN.encode(escapeQueryValue)
		resolveRecurValue = value.resolveRecur
		instance["resolveRecur"] = serder.BOOLEAN.encode(resolveRecurValue)
		from netbluemind.core.api.date.BmDateTime import BmDateTime
		from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
		dateMinValue = value.dateMin
		instance["dateMin"] = __BmDateTimeSerDer__().encode(dateMinValue)
		from netbluemind.core.api.date.BmDateTime import BmDateTime
		from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
		dateMaxValue = value.dateMax
		instance["dateMax"] = __BmDateTimeSerDer__().encode(dateMaxValue)
		resolveAttendeesValue = value.resolveAttendees
		instance["resolveAttendees"] = serder.BOOLEAN.encode(resolveAttendeesValue)
		from netbluemind.calendar.api.VEventAttendeeQuery import VEventAttendeeQuery
		from netbluemind.calendar.api.VEventAttendeeQuery import __VEventAttendeeQuerySerDer__
		attendeeValue = value.attendee
		instance["attendee"] = __VEventAttendeeQuerySerDer__().encode(attendeeValue)
		eventUidValue = value.eventUid
		instance["eventUid"] = serder.STRING.encode(eventUidValue)
		from netbluemind.core.api.date.BmDateTime import BmDateTime
		from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
		recuridValue = value.recurid
		instance["recurid"] = __BmDateTimeSerDer__().encode(recuridValue)
		anyRecurIdValue = value.anyRecurId
		instance["anyRecurId"] = serder.BOOLEAN.encode(anyRecurIdValue)
		return instance

