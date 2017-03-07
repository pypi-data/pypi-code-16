from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.rdf.Resource import Resource

from SeasObjects.model.PhysicalEntity import PhysicalEntity

import traceback

class Person(PhysicalEntity):

	def __init__(self, uri = None):
		PhysicalEntity.__init__(self, uri)
		self.setType(RESOURCE.PERSON)


	
	
