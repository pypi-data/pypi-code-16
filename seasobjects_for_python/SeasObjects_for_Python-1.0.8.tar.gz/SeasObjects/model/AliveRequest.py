from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.Tools import Tools
from SeasObjects.rdf.Resource import Resource

from SeasObjects.model.Request import Request


class AliveRequest(Request):
	
	def __init__(self, uri = None):
		Request.__init__(self, uri)
		self.setType(RESOURCE.ALIVEREQUEST)		
	
	
	
	
		
	@classmethod
	def fromString(cls, data, serialization):
		m = Tools().fromString(data, serialization)
		res = Tools().getResourceByType(RESOURCE.ALIVEREQUEST, m)
		return cls.parse(res)
		