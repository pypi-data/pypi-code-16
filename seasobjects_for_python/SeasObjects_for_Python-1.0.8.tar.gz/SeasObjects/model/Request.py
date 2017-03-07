from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.PROPERTY import PROPERTY

from SeasObjects.model.Message import Message
from SeasObjects.rdf.Resource import Resource
from SeasObjects.seasexceptions.NonePointerException import NonePointerException

import traceback
import sys
from rdflib import URIRef

class Request(Message):

	def __init__(self, uri = None):
		Message.__init__(self, uri)
		self.setType(RESOURCE.REQUEST)
		
	
	@classmethod
	def fromString(cls, data, serialization):
		from SeasObjects.common.Tools import Tools
		try:
			return cls.parse(Tools().getResourceByType(RESOURCE.REQUEST, Tools().fromString(data, serialization)));
		except:
			print "Unable to parse Request from the given string."
			traceback.print_exc() 
			return None
	
	
