from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.model.Entity import Entity
from SeasObjects.model.Evaluation import Evaluation
from SeasObjects.rdf.Resource import Resource

import sys
import traceback

class SystemOfInterest(Entity):

	def __init__(self, uri = None):
		Entity.__init__(self, uri)		
		self.realizedBy = None
		self.setType(RESOURCE.SYSTEMOFINTEREST)
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		systemOfInterest = super(SystemOfInterest, self).serialize(model)
		
		
		if self.isRealizedBy():
			systemOfInterest.addProperty(model.createProperty( PROPERTY.REALIZEDBY ), self.realizedBy.serialize(model) )

		return systemOfInterest

	def parseStatement(self, statement):
		from SeasObjects.model.PhysicalEntity import PhysicalEntity
				
		# get predicate
		predicate = str(statement.getPredicate())				
		
		# reg key
		if predicate == PROPERTY.REALIZEDBY:
			try:
				self.setRealizedBy(PhysicalEntity().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:realizedBy value as resource."
				print sys.exc_info()[1]
				traceback.print_exc() 
			return

		# pass on to Object
		super(SystemOfInterest, self).parseStatement(statement)	

	def isRealizedBy(self):
		return self.realizedBy is not None

	def getRealizedBy(self):
		return self.realizedBy
	
	def setRealizedBy(self, rb):
		self.realizedBy = rb
