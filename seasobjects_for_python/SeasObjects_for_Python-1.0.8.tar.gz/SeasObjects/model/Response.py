from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.PROPERTY import PROPERTY

from SeasObjects.rdf.Resource import Resource
from SeasObjects.model.Message import Message
from SeasObjects.seasexceptions.NonePointerException import NonePointerException

import traceback

class Response(Message):
	
	def __init__(self, uri = None):
		Message.__init__(self, uri)
		self.setType(RESOURCE.RESPONSE)

	
	@classmethod
	def fromString(cls, data, serialization):
		from SeasObjects.common.Tools import Tools
		try:
			return cls.parse(Tools().getResourceByType(RESOURCE.RESPONSE, Tools().fromString(data, serialization)))
		except:
			print "Unable to parse Response from the given string."
			traceback.print_exc() 
			return None
	
	
