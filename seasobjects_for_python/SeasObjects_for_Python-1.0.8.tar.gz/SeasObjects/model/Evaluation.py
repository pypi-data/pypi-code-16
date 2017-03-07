from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE

from SeasObjects.model.Obj import Obj
from SeasObjects.model.Map import Map
from SeasObjects.model.Service import Service

from SeasObjects.rdf.Resource import Resource
from SeasObjects.rdf.Property import Property
from SeasObjects.rdf.Statement import Statement
from SeasObjects.rdf.types import *
from rdflib import URIRef
from rdflib.namespace import RDF

from SeasObjects.seasexceptions.NonePointerException import NonePointerException

import traceback


class Evaluation(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.setType(RESOURCE.EVALUATION)
		self.categories = []
		self.entities = []
		self.timeSeries = []
		
		self.systemOfInterest = None
		self.temporalContext = None
		self.quantity = None
		self.unit = None
		self.instant = None
		self.value = None
		self.minimum = None
		self.maximum = None
		self.valueObjects = []
		self.inputs = []
		self.outputs = []
		self.interfaces = []
		self.activities = []
		self.list = []
		self.map = Map()
		
	def serialize(self, model):
		from SeasObjects.model.Input import Input
		from SeasObjects.model.Output import Output
		
		if self.serializeAsReference:
			return self.serializeToReference(model)
	
		resource = super(Evaluation, self).serialize(model)

		# categoriess
		for category in self.categories:
			resource.addProperty( model.createProperty( PROPERTY.CATEGORY ), model.createResource( category ) )

		# entities
		for entity in self.entities:
			resource.addProperty( model.createProperty( PROPERTY.ENTITY ), entity.serialize(model) )

		# timeseries
		for timeSerie in self.timeSeries:
			resource.addProperty( model.createProperty( PROPERTY.TIMESERIES ), timeSerie.serialize(model) )

		
		# systemOfInterest
		if self.hasSystemOfInterest():
			resource.addProperty(model.createProperty( PROPERTY.SYSTEMOFINTEREST ), self.systemOfInterest.serialize(model))

		# temporalcontext
		if self.hasTemporalContext():
			resource.addProperty(model.createProperty( PROPERTY.TEMPORALCONTEXT ), self.temporalContext.serialize(model))

		# set interfaces
		for iAddrs in self.interfaces:
			resource.addProperty(model.createProperty( PROPERTY.INTERFACE ), iAddrs.serialize(model))

		# quantity
		if self.hasQuantity():
			resource.addProperty(model.createProperty( PROPERTY.QUANTITYKIND ), model.createResource(self.quantity))

		# instant
		if self.hasInstant():
			resource.addProperty(model.createProperty( PROPERTY.INSTANT ), model.createLiteral(self.instant))

		# unit
		if self.hasUnit():
			resource.addProperty(model.createProperty( PROPERTY.UNIT ), model.createResource(self.unit))
		
		# value
		if self.hasValue():
			resource.addProperty(model.createProperty( PROPERTY.RDF_VALUE ), self.value.serialize(model))

		# minimum
		if self.hasMinimum():
			resource.addProperty(model.createProperty( PROPERTY.MINIMUM ), self.minimum.serialize(model))

		# maximum
		if self.hasMaximum():
			resource.addProperty(model.createProperty( PROPERTY.MAXIMUM ), self.maximum.serialize(model))

		# valueobjects
		valueobjProp = model.createProperty( PROPERTY.VALUEOBJECT )
		for valueObject in self.valueObjects:
			resource.addProperty( valueobjProp, valueObject.serialize(model) )

		# inputs
		for input in self.inputs:
			if input.getInputType() == Input.TYPE_DATA:
				resource.addProperty(model.createProperty( PROPERTY.HASINPUT ), input.serialize(model))
			if input.getInputType() == Input.TYPE_REFERENCE:
				resource.addProperty(model.createProperty( PROPERTY.HASREFINPUT ), input.serialize(model))	

		# outputs
		for output in self.outputs:
			resource.addProperty(model.createProperty( PROPERTY.HASOUTPUT ), output.serialize(model))

		# set activities
		for activity in self.activities:
			resource.addProperty(model.createProperty( PROPERTY.ACTIVITY ), activity.serialize(model))

		"""
		for parameter in self.parameters:
			resource.addProperty(model.createProperty( PROPERTY.PARAMETER ), parameter.serialize(model))
		"""
		
		# list
		if self.hasList():
			rdfList = model.createOrderedList()
			for i in range(len(self.list)):
				rdfList.add_items(self.list[i].serialize(model))
			
			listContainer = model.createResource()
			listContainer.addProperty(Property(RDF.first), rdfList)
			resource.addProperty(model.createProperty(PROPERTY.RDF_VALUE), listContainer)
			resource.addProperty(model.createProperty(PROPERTY.LIST), listContainer)

		# map
		if self.hasMap():
			resource.addProperty(model.createProperty(PROPERTY.MAP), self.map.serialize(model))
	
		return resource

	@classmethod
	def fromString(cls, data, serialization):
		from SeasObjects.common.Tools import Tools
		try :
			return cls.parse(Tools().getResourceByType(RESOURCE.EVALUATION, Tools().fromString(data, serialization)));
		except:
			print "Unable to parse Evaluation from the given string."
			traceback.print_exc()
			return None
	
	def parseStatement(self, statement):
		from SeasObjects.rdf.Variant import Variant
		from SeasObjects.model.Activity import Activity
		from SeasObjects.model.Device import Device
		from SeasObjects.model.Entity import Entity
		from SeasObjects.model.Input import Input
		from SeasObjects.model.Output import Output
		from SeasObjects.model.Parameter import Parameter
		from SeasObjects.model.ValueObject import ValueObject
		from SeasObjects.model.SystemOfInterest import SystemOfInterest
		from SeasObjects.model.TemporalContext import TemporalContext
		from SeasObjects.model.InterfaceAddress import InterfaceAddress
		from SeasObjects.model.TimeSeries import TimeSeries
		from SeasObjects.common.Tools import Tools
				
		if statement is None:
			raise NonePointerException("Unable to parse None to Evaluation.")
			return
			
		# get predicate
		predicate = str(statement.getPredicate())
		
		# category
		if predicate == PROPERTY.CATEGORY:
			try:
				self.addCategory(str(statement.getResource().toString()))
			except:
				print "Unable to interpret seas:category value as resource."
				traceback.print_exc()
			return

		# systemofinterest
		if predicate == PROPERTY.SYSTEMOFINTEREST:
			try:
				self.setSystemOfInterest(SystemOfInterest().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:systemOhInterest value as resource."
				traceback.print_exc()
			return

		# temporalcontext
		if predicate == PROPERTY.TEMPORALCONTEXT:
			try:
				self.setTemporalContext(TemporalContext().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:temporalContext value as resource."
				traceback.print_exc()
			return

		# interfaceaddress
		if predicate == PROPERTY.INTERFACE:
			try:
				self.addInterface(InterfaceAddress().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:interface value as resource."
				traceback.print_exc()
			return

		# timeserie
		if predicate == PROPERTY.TIMESERIES:
			try:
				self.addTimeSerie(TimeSeries().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:timeSeries value as resource."
				traceback.print_exc()
			return

		# quantity
		if predicate == PROPERTY.QUANTITYKIND:
			try:
				self.setQuantity(statement.getResource().toString())
			except:
				print "Unable to interpret seas:quantity value as resource."
				traceback.print_exc()
			return;

		# unit
		if predicate == PROPERTY.UNIT:
			try:
				self.setUnit(statement.getResource().toString())
			except:
				print "Unable to interpret seas:unit value as resource."
				traceback.print_exc()
			return

		# instant
		if predicate == PROPERTY.INSTANT:
			try:
				self.setInstant(statement.getObject().toPython())
			except:
				print "Unable to interpret seas:instant value as date literal."
				traceback.print_exc()
			return

		# value
		if predicate == PROPERTY.RDF_VALUE:
			self.setValue(Variant().parse(statement))
			return

		# minimum
		if predicate == PROPERTY.MINIMUM:
			self.setMinimum(Variant().parse(statement))
			return

		# maximum
		if predicate == PROPERTY.MAXIMUM:
			self.setMaximum(Variant().parse(statement))
			return

		# valueobject
		if predicate == PROPERTY.VALUEOBJECT:
			try:
				self.addValueObject(ValueObject().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:valueObject value as resource."
				traceback.print_exc()
			return

		# input data
		if predicate == PROPERTY.HASINPUT:
			try:
				self.addInput(Input().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:hasInput value as resource."
				traceback.print_exc()
			return

		# input reference
		if predicate == PROPERTY.HASREFINPUT:
			try:
				input = Input().parse(statement.getResource())
				input.setInputType(Input.TYPE_REFERENCE)
				self.addInput(input)
			except:
				print "Unable to interpret seas:hasRefInput value as resource."
				traceback.print_exc()
			return

		# output
		if predicate == PROPERTY.HASOUTPUT:
			try:
				self.addOutput(Output().parse(statement.getResource()));
			except:
				print "Unable to interpret seas:hasOutput value as resource."
				traceback.print_exc()
			return
		
		# activities
		if predicate == PROPERTY.ACTIVITY:
			try:
				self.addActivity(Activity().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:activity value as resource."
				traceback.print_exc()
			return
		
		""""
		if predicate == PROPERTY.PARAMETER:
			try:
				self.addParameter(Parameter().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:parameter value as resource."
				traceback.print_exc()
			return
		"""
		
		# entity
		if predicate == PROPERTY.ENTITY:
			types = None
			try:
				types = Tools().getResourceTypes(statement.getResource())
			except:
				print "Unable to interpret seas:entity value as resource."
				traceback.print_exc()

			# service
			if types is not None and RESOURCE.SERVICE in types:
				try:
					self.addEntity(Service().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:entity value (of type seas:Service) as resource."
					traceback.print_exc()
				return

			# device
			if types is not None and RESOURCE.DEVICE in types:
				try:
					self.addEntity(Device().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:entity value (of type seas:Device) as resource."
					traceback.print_exc()
				return
			
			
			# serviceprovider
			
			# weatherserviceprovider
			
			# could not match with any entity subtype
			try:
				self.addEntity(Entity().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:entity value (of type seas:Entity) as resource."
				traceback.print_exc()
			return

		

		# generatedat
		if predicate == PROPERTY.LIST:
			try:
				self.setList(statement.getResource().toList(Evaluation))
			except:
				print "Unable to interpret seas:list value as list."
				traceback.print_exc()
			return

		# generatedat
		if predicate == PROPERTY.MAP:
			try:
				self.setMap(Map().parse(statement.getResource()))
			except:
				print "Unable to interpret seas:map value as resource."
				traceback.print_exc()
			return

		# pass on to Obj
		super(Evaluation, self).parseStatement(statement)


	def hasInput(self):
		return len(self.inputs) > 0
	
	def getInputs(self):
		return self.inputs
	
	def setInput(self, input):
		self.inputs = [input]
	
	def addInput(self, input):
		self.inputs.append(input)

	def firstInput(self):
		try:
			return self.inputs[0]
		except:
			return None
		
	def hasOutput(self):
		return len(self.outputs) > 0

	def getOutputs(self):
		return self.outputs
	
	def setOutput(self, output):
		self.outputs = [output]

	def addOutput(self, output):
		self.outputs.append(output)

	def firstOutput(self):
		try:
			return self.outputs[0]
		except:
			return None
		
	

	def hasCategory(self):
		return len(self.categories) > 0

	def setCategory(self, category):
		self.categories = [category]

	def addCategory(self, category):
		self.categories.append(category)

	def getCategories(self):
		return self.categories

	def hasEntities(self):
		return len(self.entities) > 0

	def setEntity(self, entity):
		self.entities = [entity]

	def addEntity(self, entity):
		self.entities.append(entity)

	def getEntities(self):
		return self.entities

	def hasValueObject(self):
		return len(self.valueObjects) > 0
	
	def setValueObject(self, valueObject):
		self.valueObjects = [valueObject]

	def addValueObject(self, valueObject):
		self.valueObjects.append(valueObject)

	def getValueObjects(self):
		return self.valueObjects

	def hasTimeSeries(self):
		return len(self.timeSeries) > 0
	
	def getTimeSeries(self):
		return self.timeSeries
	
	def setTimeSerie(self, timeSerie):
		self.timeSeries = [timeSerie]

	def addTimeSerie(self, timeSerie):
		self.timeSeries.append(timeSerie)

	def hasSystemOfInterest(self):
		return self.systemOfInterest is not None

	def getSystemOfInterest(self):
		return self.systemOfInterest

	def setSystemOfInterest(self, system):
		self.systemOfInterest = system
		
	def setSystemOfInterestWithSameAs(self, sameAs):
		from SeasObjects.model.SystemOfInterest import SystemOfInterest
		'''
		@param sameAs: a String representing the sameAs URI 
		'''
		soi = SystemOfInterest()
		soi.setSameAs(sameAs)
		self.systemOfInterest = soi		

	def hasTemporalContext(self):
		return self.temporalContext is not None

	def getTemporalContext(self):
		return self.temporalContext

	def setTemporalContext(self, temporalContext):
		self.temporalContext = temporalContext

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

	def hasInstant(self):
		return self.instant is not None
	
	def getInstant(self):
		return self.instant

	def setInstant(self, instant):
		self.instant = instant

	def hasValue(self):
		return self.value is not None
	
	def getValue(self):
		return self.value

	def setValue(self, value):
		self.value = value

	def hasMinimum(self):
		return self.minimum is not None
	
	def getMinimum(self):
		return self.minimum

	def setMinimum(self, minimum):
		self.minimum = minimum

	def hasMaximum(self):
		return self.maximum is not None
	
	def getMaximum(self):
		return self.maximum

	def setMaximum(self, maximum):
		self.maximum = maximum

	

	def getInterfaces(self):
		return self.interfaces

	def setInterface(self, interfaceAddress):
		self.interfaces = [interfaceAddress]

	def addInterface(self, interfaceAddress):
		self.interfaces.append(interfaceAddress)

	def hasActivity(self):
		return len(self.activities) > 0
	
	def getActivities(self):
		return self.activities

	def setActivity(self, activity):
		self.activities = [activity]

	def addActivity(self, activity):
		self.activities.append(activity)
	
	def firstActivity(self):
		try:
			return self.activities[0]
		except:
			return None
		
	"""
	def getParameters(self):
		return self.parameters

	def setParameter(self, p):
		self.parameters = [p]
	"""
	
	def addParameter(self, p):
		self.add(URIRef(PROPERTY.PARAMETER), p)

	def hasList(self):
		return len(self.list) > 0
	
	def getList(self):
		return self.list
	
	def setList(self, _list):
		self.list = _list;
		
	def addListItem(self, i):
		self.list.append(i)
		
	def hasMap(self):
		return not self.map.isEmpty()
	
	def getMap(self):
		return self.map
	
	def setMap(self, _map):
		self.map = _map
	
