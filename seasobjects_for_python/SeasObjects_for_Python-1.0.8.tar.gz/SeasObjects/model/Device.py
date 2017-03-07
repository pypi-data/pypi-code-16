from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.model.PhysicalEntity import PhysicalEntity
from SeasObjects.rdf.Resource import Resource

import traceback

class Device(PhysicalEntity):

	def __init__(self, uri = None):
		PhysicalEntity.__init__(self, uri)
		self.managingSystemUri = None
		self.setType(RESOURCE.DEVICE);
	
	def hasManagingSystemUri(self):
		return self.managingSystemUri is not None

	def setManagingSystemUri(self, uri):
		self.managingSystemUri = uri
	
	def getManagingSystemUri(self):
		return self.managingSystemUri

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		device = super(Device, self).serialize(model)

		# set system uri
		if self.hasManagingSystemUri():
			system = model.createResource( self.managingSystemUri )
			device.addProperty(model.createProperty( PROPERTY.ISMANAGEDBY ), system)

		return device

	def parseStatement(self, statement):
		
			predicate = str(statement.getPredicate())

			# ismanagedby
			if predicate == PROPERTY.ISMANAGEDBY:
				try:
					self.setManagingSystemUri(statement.getString())
				except:
					print "Unable to interpret seas:isManagedBy value as resource."
					traceback.print_exc()
				return 
			
			# pass on to Object
			super(Device, self).parseStatement(statement)

