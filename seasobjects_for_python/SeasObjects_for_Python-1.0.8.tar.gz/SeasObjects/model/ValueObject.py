from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.model.Obj import Obj
from SeasObjects.rdf.Variant import Variant

from rdflib import URIRef
import traceback


class ValueObject(Obj):

	def __init__(self, uri = None, quantity = None, unit = None, value = None, maximum = None, minimum = None):
		Obj.__init__(self, uri)
		if quantity is not None and not isinstance(quantity, URIRef): quantity = URIRef(quantity)
		if unit is not None and not isinstance(unit, URIRef): unit = URIRef(unit)
		if value is not None and not isinstance(value, Variant): value = Variant(value)
		if maximum is not None and not isinstance(maximum, Variant): maximum = Variant(maximum)
		if minimum is not None and not isinstance(minimum, Variant): minimum = Variant(minimum)
		self.quantity = quantity
		self.unit = unit
		self.value = value
		self.maximum = maximum
		self.minimum = minimum
		self.setType(RESOURCE.VALUEOBJECT)

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		valueObject = super(ValueObject, self).serialize(model)

		# quantity
		if self.hasQuantity():
			quantity = model.createResource(self.quantity)
			valueObject.addProperty(model.createProperty( PROPERTY.QUANTITYKIND ), self.quantity)
		
		# unit
		if self.hasUnit():
			unit = model.createResource(self.unit)
			valueObject.addProperty(model.createProperty( PROPERTY.UNIT ), self.unit)

		# value
		if self.hasValue():
			valueObject.addProperty(model.createProperty( PROPERTY.RDF_VALUE ), self.value.serialize(model))
			
		if self.hasMaximum():
			valueObject.addProperty(model.createProperty( PROPERTY.MAXIMUM ), self.value.serialize(model))
		
		if self.hasMinimum():
			valueObject.addProperty(model.createProperty( PROPERTY.MINIMUM ), self.value.serialize(model))
		
		
		return valueObject
	
	
	def parseStatement(self, statement):
		from SeasObjects.rdf.Resource import Resource
	
		# get predicate
		predicate = str(statement.getPredicate())
		
		# quantity
		if predicate == PROPERTY.QUANTITYKIND:
			try:
				self.setQuantity(statement.getResource().toString());
			except:
				print "Unable to interpret seas:quantity value as resource."
				traceback.print_exc() 

		# unit
		if predicate == PROPERTY.UNIT:
			try:
				self.setUnit(statement.getResource().toString())
			except:
				print "Unable to interpret seas:unit value as resource."
				traceback.print_exc() 
		
		# value
		if predicate == PROPERTY.RDF_VALUE:
			self.setValue(Variant().parse(statement))
			
		if predicate == PROPERTY.MAXIMUM:
			self.setMaximum(Variant().parse(statement))
			
		if predicate == PROPERTY.MINIMUM:
			self.setMinimum(Variant().parse(statement))

		# pass on to Obj
		super(ValueObject, self).parseStatement(statement)
		

	def hasQuantity(self):
		return self.quantity is not None

	def getQuantity(self):
		return self.quantity
	
	def setQuantity(self, quantity):
		self.quantity = URIRef(quantity)

	def hasUnit(self):
		return self.unit is not None

	def getUnit(self):
		return self.unit
	
	def setUnit(self, unit):
		self.unit = URIRef(unit)

	def hasValue(self):
		return self.value is not None
	
	def getValue(self):
		return self.value

	def setValue(self, value):
		self.value = value
		
	def hasMaximum(self):
		return self.maximum is not None
	
	def getMaximum(self):
		return self.maximum
	
	def setMaximum(self, max):
		self.maximum = max
		
	def hasMinimum(self):
		return self.minimum is not None
	
	def getMinimum(self):
		return self.minimum
	
	def setMinimum(self, min):
		self.minimum = min