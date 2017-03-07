from SeasObjects.common.RESOURCE import RESOURCE

from SeasObjects.model.Ability import Ability
from SeasObjects.rdf.Resource import Resource

class Availability(Ability):

	def __init__(self, uri = None):
		Ability.__init__(self, uri)
		self.setType(RESOURCE.AVAILABILITY);
		
	
