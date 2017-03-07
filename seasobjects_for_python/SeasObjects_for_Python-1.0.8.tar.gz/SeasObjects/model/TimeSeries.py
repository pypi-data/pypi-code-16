from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.rdf.Resource import Resource
from SeasObjects.rdf.Property import Property
from SeasObjects.model.Obj import Obj
from SeasObjects.model.Evaluation import Evaluation
from SeasObjects.model.SystemOfInterest import SystemOfInterest
from SeasObjects.model.TemporalContext import TemporalContext

import traceback

from rdflib import XSD
from rdflib.namespace import RDF


class TimeSeries(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.quantity = None
		self.unit = None
		self.timeStep = None
		self.list = []
		self.systemOfInterest = None
		self.temporalContext = None
		self.setType(RESOURCE.TIMESERIES)

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		ts = super(TimeSeries, self).serialize(model);

		# quantity
		if self.hasQuantity():
			quantity = model.createResource(self.quantity)
			ts.addProperty(model.createProperty( PROPERTY.QUANTITYKIND ), quantity)
		
		# unit
		if self.hasUnit():
			unit = model.createResource(self.unit)
			ts.addProperty(model.createProperty( PROPERTY.UNIT ), unit)

		# timestep
		if self.hasTimeStep():
			ts.addProperty(model.createProperty( PROPERTY.TIMESTEP ), model.createTypedLiteral(self.getTimeStep(), XSD.duration))
	
		# list
		if self.hasList():			
			rdfList = model.createOrderedList()
			rdfList.add_items(self.list)
			
			listContainer = model.createResource()
			listContainer.addProperty(Property(RDF.first), rdfList)
			
			ts.addProperty(model.createProperty( PROPERTY.LIST ), listContainer)

		# systemOfInterest
		if self.hasSystemOfInterest():
			ts.addProperty(model.createProperty( PROPERTY.SYSTEMOFINTEREST ), self.systemOfInterest.serialize(model))

		# temporalcontext
		if self.hasTemporalContext():
			ts.addProperty(model.createProperty( PROPERTY.TEMPORALCONTEXT ), self.temporalContext.serialize(model))

		return ts;

	def parseStatement(self, statement):
					
			# get predicate
			predicate = str(statement.getPredicate())

			# quantity
			if predicate == PROPERTY.QUANTITYKIND:
				try:
					self.setQuantity(statement.getResource().toString())
				except:
					print "Unable to interpret seas:quantity value as resource."
					traceback.print_exc() 
				return
			
			# unit
			if predicate == PROPERTY.UNIT:
				try:
					self.setUnit(statement.getResource().toString())
				except:
					print "Unable to interpret seas:unit value as resource."
					traceback.print_exc() 
				return
			
			# timestep
			if predicate == PROPERTY.TIMESTEP:
				try:
					self.setTimeStep(statement.getString());
				except:
					print "Unable to interpret seas:timeStep value as literal string."
					traceback.print_exc() 
				return
			
			# list
			if predicate == PROPERTY.LIST:				
				try:					
					self.setList(statement.getResource().toList(Evaluation))
				except:
					print "Unable to interpret seas:list value as resource."					
				return
			
			# systemofinterest
			if predicate == PROPERTY.SYSTEMOFINTEREST:
				try:
					self.setSystemOfInterest(SystemOfInterest().parse(statement.getResource()))
				except:
					print "Unable to interpret seas:systemOfInterest value as resource."
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
			
			# pass on to Object
			super(TimeSeries, self).parseStatement(statement)
		


	def hasQuantity(self):
		return self.quantity is not None

	def getQuantity(self):
		return self.quantity
	
	def setQuantity(self, quantity):
		self.quantity = quantity

	def hasUnit(self):
		return self.unit is not None

	def getUnit(self):
		return self.unit
	
	def setUnit(self, unit):
		self.unit = unit

	def hasTimeStep(self):
		return self.timeStep is not None
	
	def getTimeStep(self):
		return self.timeStep
	
	def setTimeStep(self, timeStep):
		self.timeStep = timeStep

	def hasList(self):
		return len(self.list) > 0
	
	def getList(self):
		return self.list

	def setList(self, list):
		self.list = list

	def addListItem(self, evaluation):
		self.list.append(evaluation)

	def hasSystemOfInterest(self):
		return self.systemOfInterest is not None

	def getSystemOfInterest(self):
		return self.systemOfInterest

	def setSystemOfInterest(self, system):
		self.systemOfInterest = system

	def hasTemporalContext(self):
		return self.temporalContext is not None

	def getTemporalContext(self):
		return self.temporalContext

	def setTemporalContext(self, temporalContext):
		self.temporalContext = temporalContext
