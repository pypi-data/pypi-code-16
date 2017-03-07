from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.model.Obj import Obj
from SeasObjects.common.RESOURCE import RESOURCE

from SeasObjects.rdf.Resource import Resource
from SeasObjects.rdf.types import *
from rdflib import XSD

import traceback

class Zone(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.zoneNUmber = None
		self.setType(RESOURCE.ZONE)

	def hasZoneNumber(self):
		return self.zoneNumber is not None
	
	def getZoneNumber(self):
		return self.zoneNumber

	def setZoneNumber(self, zoneNumber):
		self.zoneNumber = zoneNumber

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		resource = super(Zone, self).serialize(model)
	
		# set zone
		if self.hasZoneNumber():
			resource.addProperty(model.createProperty( PROPERTY.ZONENUMBER ), self.zoneNumber)

		return resource


	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# country
			if predicate == PROPERTY.ZONENUMBER:
				try:
					self.setZoneNumber(statement.getString());
				except:
					print "Unable to interpret seas:zoneNumber value as literal string."
					traceback.print_exc()
				return
		
			# pass on to Object
			super(Zone, self).parseStatement(statement)
	
