from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.Tools import Tools
from SeasObjects.model.Obj import Obj
from SeasObjects.rdf.Variant import Variant

from SeasObjects.rdf.Resource import Resource
from SeasObjects.rdf.Property import Property
from SeasObjects.rdf.LinkedList import LinkedList
from SeasObjects.rdf.types import *
from rdflib import Literal
from rdflib.namespace import RDF

import traceback

class Parameter(Obj):

	def __init__(self, key = None, value = None):
		Obj.__init__(self)
		self.setType(RESOURCE.PARAMETER)
		self.key = key
		self.values = []
		
	def hasKey(self):
		return self.key is not None
	
	def setKey(self, k):
		self.key = k
	
	def getKey(self):
		return self.key
	
	def hasValue(self):
		return len(self.values) > 0
	
	def setValue(self, v):
		self.values = [v]
	
	def addValue(self, v):
		self.values.append(v)
	
	def getFirstValue(self):
		return self.values[0]
	
	def getValues(self):
		return self.values
	
	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		resource = super(Parameter, self).serialize(model)
	
		if self.hasKey():
			resource.addProperty(model.createProperty( PROPERTY.KEY ), Literal(self.getKey()))
		
		for value in self.values:
			if isinstance(value, Obj) or isinstance(value, Variant):
				resource.addProperty(model.createProperty( PROPERTY.RDF_VALUE ), value.serialize(model))
			elif isinstance(value, list):
				rdfList = model.createOrderedList()
				rdfList.add_items(value)
				listContainer = model.createResource()
				listContainer.addProperty(Property(RDF.first), rdfList)
				resource.addProperty(model.createProperty(PROPERTY.RDF_VALUE), listContainer)
			else:
				resource.addProperty(model.createProperty(PROPERTY.RDF_VALUE), Literal(value))
		return resource


	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
			
			if predicate == PROPERTY.KEY:
				
				try:
					self.setKey(statement.getString())
				except:
					print "Unable to interpret seas:key value as literal for Parameter."
					traceback.print_exc()
				return
			
			if predicate == PROPERTY.RDF_VALUE:
				target_class = Tools().getResourceClass(statement.getResource())

				if target_class is not None:
					try:
						self.addValue(target_class().parse(statement.getResource()))
					except:
						print "Unable to interpret rdf:value as value for Parameter."
						traceback.print_exc()
					return
				elif statement.getResource().model.is_list(statement.getObject()):
					l = []
					statement.getResource().model.parse_list(l, statement.getObject())
					self.addValue(l)
				else:
					self.addValue(Variant().parse(statement))
				return
			
			# pass on to Object
			super(Parameter, self).parseStatement(statement)

