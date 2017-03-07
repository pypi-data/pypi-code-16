from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.model.AbstractEntity import AbstractEntity
from SeasObjects.rdf.Resource import Resource
from SeasObjects.common.RESOURCE import RESOURCE

import traceback

class ServiceProvider(AbstractEntity):

	def __init__(self, uri = None):
		AbstractEntity.__init__(self, uri)
		self.services = []
		self.setType(RESOURCE.SERVICEPROVIDER)

	def setService(self, service):
		self.services = [service]
	
	def addService(self, service):
		self.services.append(service)

	def getServices(self):
		return self.services

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		entity = super(ServiceProvider, self).serialize(model);
		
		# set services
		offersService = model.createProperty( PROPERTY.OFFERSSERVICE )
		for service in self.services:
			entity.addProperty( offersService, service.serialize(model) )
		
		return entity
	
	def parseStatement(self, statement):
		from SeasObjects.model.Service import Service
				
		# get predicate
		predicate = str(statement.getPredicate())

		# offersservice
		if predicate == PROPERTY.OFFERSSERVICE:
			try:
				self.addService(Service().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:offersService value as resource."
				traceback.print_exc() 
			
			return

		# pass on to Object
		super(ServiceProvider, self).parseStatement(statement)
