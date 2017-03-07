from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.rdf.Resource import Resource

from SeasObjects.model.Entity import Entity

import traceback


class Organization(Entity):

	def __init__(self, uri = None):
		Entity.__init__(self, uri)
		self.setType(RESOURCE.ORGANIZATION)



	

