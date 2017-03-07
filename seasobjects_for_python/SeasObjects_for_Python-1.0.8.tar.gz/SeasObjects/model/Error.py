from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.model.Obj import Obj


class Error(Obj):
	
	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.message = None
		self.code = 0
		self.setType(RESOURCE.ERROR);
	
	def setErrorMessage(self, em):
		self.message = em
	
	def getErrorMessage(self):
		return self.message
	
	def setErrorCode(self, ec):
		self.code = ec
	
	def getErrorCode(self):
		return self.code
	
	def hasErrorCode(self):
		return self.code > 0
	
	def hasErrorMessage(self):
		return self.message != None
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		error = super(Error, self).serialize(model)
		
		if self.hasErrorMessage():
			error.addProperty(model.createProperty( PROPERTY.ERRORMESSAGE ), model.createLiteral(self.getErrorMessage()))
		
		if self.hasErrorCode():
			error.addProperty(model.createProperty( PROPERTY.ERRORCODE ), model.createLiteral(self.getErrorCode()))
		
		return error
	
	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())

			# managedby
			if predicate == PROPERTY.ERRORMESSAGE:
				self.message = statement.getResource().toString()
				return

			# interfaceaddress
			if predicate == PROPERTY.ERRORCODE:
				self.code = int(statement.getResource().toString())
				return

			# pass on to Object
			super(Error, self).parseStatement(statement)
		
		
