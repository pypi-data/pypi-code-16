from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.Tools import Tools

#from SeasObjects.model.Controllability import Controllability
#from SeasObjects.model.Availability import Availability

from SeasObjects.model.Obj import Obj
from SeasObjects.rdf.Resource import Resource
from SeasObjects.rdf.Variant import Variant
import traceback


class Condition(Obj):

	def __init__(self, uri = None):
		Obj.__init__(self, uri)
		self.regexes = []
		self.ors = []
		self.ands = []
		self.setType(RESOURCE.CONDITION)

	def serialize(self, model):
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		resource = super(Condition, self).serialize(model)

		# regexes
		regexProp = model.createProperty( PROPERTY.REGEX )
		for regex in self.regexes:
			resource.addProperty( regexProp, model.createLiteral(regex) )

		# ors
		orProp = model.createProperty( PROPERTY.OR )
		for o in self.ors:
			resource.addProperty( orProp, o.serialize(model) )

		# ands
		andProp = model.createProperty( PROPERTY.AND )
		for a in self.ands:
			resource.addProperty( andProp, a.serialize(model) )

		return resource


	def parseStatement(self, statement):
		
			# get predicate
			predicate = str(statement.getPredicate())
	
			# regex
			if predicate.equals(PROPERTY.REGEX):
				try:
					self.addRegex(statement.getString())
				except:
					print "Unable to interpret seas:regex value as literal string."
					traceback.print_exc()
				return
	
			# or
			if predicate.equals(PROPERTY.OR):
				try:
					self.addOr(Variant().parse(statement))
				except:
					print "Unable to interpret seas:or value as resource."
					traceback.print_exc()
				return

			# and
			if predicate.equals(PROPERTY.AND):				
				try:
					self.addAnd(Variant().parse(statement))
				except:
					print "Unable to interpret seas:and value as resource."
					traceback.print_exc()

				return
	
			# pass on to Obj
			super(Condition, self).parseStatement(statement)

	def hasOr(self):
		return len(self.ors) > 0

	def getOrs(self):
		return self.ors

	def addOr(self, o):
		self.ors.append(o)

	def hasAnd(self):
		return len(self.ands) > 0

	def getAnds(self):
		return self.ands

	def addAnd(self, a):
		self.ands.append(a)

	def hasRegex(self):
		return len(self.regexes) > 0

	def getRegexes(self):
		return self.regexes

	def addRegex(self, regex):
		self.regexes.append(regex)
