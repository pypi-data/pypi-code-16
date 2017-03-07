from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.VARIANT import VARIANT
from SeasObjects.model.Obj import Obj
from SeasObjects.rdf.Resource import Resource
from SeasObjects.common.Tools import Tools

from rdflib import Literal, BNode, URIRef

import datetime


class Variant(object):

	def __init__(self, value = None):
		self.variant = value
	
	def serialize(self, model):
		if self.isObj() or self.isVariant():
			return self.variant.serialize(model)
		else:
			return self.asTerm()

	def asTerm(self):
		if self.isUri():
			return self.variant
		elif self.isNull():
			return None
		else:
			return Literal(self.variant)

	def parse(self, statement):
		# get predicate and object
		predicate = str(statement.getPredicate())
		objectNode = statement.getObject()

		# if literal object
		dataType = None
		if isinstance(objectNode, Literal):
			return Variant(objectNode.toPython())
		
		elif (statement.getResource() is not None):
			resource = statement.getResource()
			klass = Tools().getResourceClass(resource, default = Obj)
			if klass is not None:
				v = klass().parse(resource)
			else:
				# None found, resort to Obj (the base class)
				v = Obj().parse(resource)
			
			return v
			
		elif isinstance(objectNode, BNode):
			l = []
			statement.getResource().getModel().parse_list(l, objectNode, None)
			return l
		
		elif isinstance(objectNode, URIRef):
			return Variant(objectNode)
					
		# could not identify datatype
		print "Parsing variant failed. Unable to detect RDFDatatype (" + str(dataType) + ") for literal."
		return Variant("");


	def isNull(self):
		return self.variant is None

	def isUri(self):
		return isinstance(self.variant, URIRef)
	
	def isString(self):
		return isinstance(self.variant, str)
	
	def isInteger(self):
		return isinstance(self.variant, int)

	def isDouble(self):
		return isinstance(self.variant, float)
		
	def isFloat(self):
		return isinstance(self.variant, float)

	def isBoolean(self):
		return isinstance(self.variant, bool)

	def isDate(self):
		return isinstance(self.variant, datetime.date)

	def isTime(self):
		return isinstance(self.variant, datetime.time)
	
	def isDateTime(self):
		return isinstance(self.variant, datetime.datetime)
	
	def isMap(self):
		from SeasObjects.model.Map import Map
		return isinstance(self.variant, Map)
	
	def isObj(self):
		return isinstance(self.variant, Obj)
	
	def isVariant(self):
		return isinstance(self.variant, Variant)

	def getValue(self):
		if isinstance(self.variant, Literal):
			return self.variant.toPython()
		return self.variant

	def getType(self):
		print self.variant
		if self.isNull():
			return "Null"
		elif self.isUri():
			return "Uri"
		elif self.isString():
			return "string"
		elif self.isInteger():
			return "int"
		elif self.isDouble():
			return "double"
		elif self.isFloat():
			return "float"
		elif self.isBoolean():
			return "boolean"
		elif self.isDate():
			return "date"
		elif self.isTime():
			return "time"
		elif self.isDateTime():
			return "datetime"
		elif self.isMap():
			return "Map"
		elif self.isObj():
			return "Obj"
		elif self.isVariant():
			return "Variant"
		return "Null"

	def getAsString(self):
		return str(self.variant)

	# Most method below have no significance in Python as the language
	# is not strongly typed. They are however offered as convenience
	# to make implementions between different languages as similar
	# as possible
	def asString(self):
		return self.getAsString()
	
	def asObj(self):
		return self.variant

	def asInt(self):
		try:
			return int(self.variant)
		except:
			return 0
		
	def asDouble(self):
		try:
			return float(self.variant)
		except:
			return 0
		
	def asFloat(self):
		try:
			return float(self.variant)
		except:
			return 0

	def asBoolean(self):
		return self.variant
		
	def asDate(self):
		try:
			return Tools().stringToDate(str(self.variant)).date()
		except:
			return None
		
	def asTime(self):
		try:
			return Tools().stringToDate(str(self.variant)).time()
		except:
			return None
	
	def __repr__(self):
		return "<Variant:: type: %s, value: %s>"%(self.getType(), self.getValue())
