from SeasObjects.factory.Factory import Factory
from SeasObjects.rdf.Property import Property
from SeasObjects.rdf.Resource import Resource
from SeasObjects.rdf.LinkedList import LinkedList
from SeasObjects.rdf.OrderedList import OrderedList
from SeasObjects.rdf.ItemizedList import ItemizedList
from SeasObjects.rdf.NudeList import NudeList
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.CONTENTTYPES import CONTENTTYPE
from SeasObjects.common.ClassMapper import ClassMapper
from SeasObjects.common.HttpMessage import HttpMessage
from SeasObjects.common.HttpMessage import HttpMessageSingle
from SeasObjects.common.HttpMessage import parseMIMEmessage
from SeasObjects.common.SERIALIZATION import SERIALIZATION
from SeasObjects.common.RESOURCE import RESOURCE


from SeasObjects.seasexceptions.NotFoundException import NotFoundException
from rdflib import URIRef
from rdflib.namespace import RDF

import traceback
import datetime


class Tools(object):

	def __init__(self):
		self.mapper = ClassMapper()
	
	@classmethod	
	def toString(cls, element, serialization='text/turtle'):
		'''
		serialize Seas Obj or its subclass Obj to string. 
		'''
		model = Factory().createModel()
		
		if isinstance(element, list) or isinstance(element, LinkedList) or isinstance(element, OrderedList) or isinstance(element, ItemizedList) or isinstance(element, NudeList):
			# Raw top level list. We need some blank node to hold the list
			top_element = Resource(model = model)
			top_element.addProperty(Property(RDF.first), element)
			cls.addRecursivelyToModel(top_element, model)
		else:
			cls.addRecursivelyToModel(element, model)
		
		# serialize
		messageBody = ""
		try:
			messageBody = model.serialize(format=serialization)
		except:
			print "Exception while converting model into string"
			traceback.print_exc()

		return messageBody

	@classmethod
	def fromString(cls, strng, serialization = None):
		model = Factory().createModel()
		try:
			model.parse(data = strng, format=serialization)
		except:
			print "Could not parse the input into a model"
			traceback.print_exc()
		return model
	
	def fromFile(self, filename, serialization):
		model = Factory.createModel()

		try:
			f = open(filename)
			model.parse(file = filename, format=serialization)
			f.close()
		except:
			print "Could not read the file into a model"
			traceback.print_exc()
			
		return model
	
	def fromStringAsObj(self, strng, serialization = None, isType = None):
		model = self.fromString(strng, serialization = serialization)
		if isType is None:
			node, isType = self.getTopNode(model)
		
		res = self.getResourceByType(isType, model)
		cm = ClassMapper()
		obj = cm.getClass([str(isType)])()
		sl = node.findProperties()
		for s in sl:
			obj.parseStatement(s)
		return obj;
	
	def fromStringAsList(self, strng, serialization = None, isType = None):
		model = self.fromString(strng, serialization = serialization)
		sl = model.listStatements(subject = None, predicate = URIRef(RDF.first), object = None)
		list_container = []
		# Find the "orphan" rdf.first node, this is the starting point of all lists
		for s in sl:
			ss = model.listStatements(subject = None, predicate = None, object = s.getSubject())
			if len(ss) == 0:
				model.parse_list(list_container, parent_node = s.getSubject(), first = s.getObject())
				break
		
		return list_container
	
	
	def toObj(self, objStr):
		'''
		@param objStr: string presentation of Seas Obj. Currently only consider turtle serialization.
		@return: The Obj or its subclass Object
		'''
		model = self.fromString(objStr, SERIALIZATION.TURTLE)
		rootRes = self.getTopNode(model)[0]
		seasCls = self.getResourceClass(rootRes)
		recoveredObj =  seasCls.parse(rootRes)
		return recoveredObj
		
		
	def getSerializationForContentType(self, content_type):
		if CONTENTTYPE.mapping.has_key(content_type):
			return CONTENTTYPE.mapping[content_type]
		return "Unknown"
	
	@classmethod
	def addRecursivelyToModel(cls, resource, model):
		from SeasObjects.model.Obj import Obj
		
		# add this level statements
		if isinstance(resource, Obj):
			model.add(resource.serialize(model))
		elif isinstance(resource, list):
			for item in resource:
				cls.addRecursivelyToModel(item, model)
		else:
			model.add(resource)

	
		
	"""
	 Convert Python datetime to xsd:dateTime string
	 @param dateTime timestamp to convert
	 @return xsd:dateTime stype string
	"""
	def dateToString(self, date_time):
		ret = None
		try:
			ret = date_time.strftime("%Y-%m-%dT%H:%M:%S")
		except:
			print "Error while converting zoned datetime to ISO offset datetime string"
		return ret
	

	def stringToDate(self, date_str):
		date = None
		try:
			date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
		except:
			print "Error while converting ISO offset datetime string to zoned datetime"
		return date
		

	def stripUri(self, uri):
		stripped = uri
		splits = uri.split("#", 1)
		if len(splits) > 1:
			stripped = splits[1]
		return stripped;
	
	@classmethod	
	def getResourceByType(cls, type, model):
		return model.findSubject(URIRef(PROPERTY.RDF_TYPE), URIRef(type))

	"""
	def getResourceByType(self, type, model):
		typeResource = model.createResource(type)
		typeProperty = model.createProperty(PROPERTY.RDF_TYPE)

		s = model.listStatements(None, typeProperty, typeResource)
		if len(s) > 0:
			r = Resource(model, s.getSubject())
			return r
		else:
			raise NotFoundException("Could not find resource by type " + type + " from the provided model.")
	"""
	
	def getResourceType(self, resource):
		object = resource.getPropertyResourceValue(resource.getModel().createProperty(PROPERTY.RDF_TYPE))
		if ( object is not None ):
			return object.toString()
		return None

	def getResourceTypes(self, resource):
		types = []
		for statement in resource.findProperty(resource.getModel().createProperty(PROPERTY.RDF_TYPE)):
			types.append(statement.getResource().toString())
		return types
	
	
	def getResourceClass(self, resource, default = None):
		types = self.getResourceTypes(resource)
		return self.mapper.getClass(types, default = default)

	@classmethod
	def getTopNode(cls, model):
		# Find the top node of a received structure. To do this, find all triples where
		# the subject is not the object of anything.
		# These subjects are the resources of orphan nodes. Because we are eventually
		# looking for the RDF type of the objects, it is enough to iterate the nodes
		# that contain an RDF type attribute
		nodeType = None
		node = None
		sl = model.listStatements(subject = None, predicate = URIRef(PROPERTY.RDF_TYPE), object = None)
		for s in sl:
			nodeType = s.getObject()
			ss = model.listStatements(subject = None, predicate = None, object = s.getSubject())
			if len(ss) == 0:
				node = Resource(model = model, node = s.getSubject())
				break
		if node is not None:
			return node, nodeType
		raise NotFoundException("Could not find any orphan objects from the provided model.")
	
	@classmethod
	def serializeRequest(cls, message, serialization = 'text/turtle'):
		return cls.serializeMessage(message, serialization)
	@classmethod
	def serializeResponse(cls, message, serialization = 'text/turtle'):
		return cls.serializeMessage(message, serialization)
	@classmethod
	def serializeMessage(cls, message, serialization = 'text/turtle'):
		'''
		Extended version of Tools.toString() method. This method takes a Request or Response Object as input, return MIME message (multipart or single part). 
		@return: two strings, one is the serialized message together with MIME headers(i.e., Content-Type header);
		the other is the Content-Type header 
				
		'''	
		Tools.messageParts.clear()
		# this step might add new items to Tools.messageParts.					
		messageString = cls.toString(message, serialization)
		# multipart or single part generation goes here. 		
		if len(Tools.messageParts)==0:
			httpMessageSingle = HttpMessageSingle()
			httpMessageSingle.add(messageString, serialization)	
					
			return (httpMessageSingle.asString(), httpMessageSingle.getContentType())
		else: # add messageString and additional messageParts into multipart
			httpMessage= HttpMessage()
			httpMessage.addMainpart(messageString, serialization)
			for partId in Tools.messageParts.keys():
				httpMessage.add(partId, Tools.messageParts.get(partId), serialization)	
			Tools.messageParts.clear()
			
			return (httpMessage.asString(), httpMessage.getContentType())
	
	@classmethod
	def parseRequest(cls, content):
		'''
		Extended version of Request/Response.fromString() method. It can handle both multipart and singlepart. It is supposed to
		be used after serializeRequest() call.
		
		@param content: message body with Content-Type headers as a String
		@return: a Request Object. 
		'''
		from SeasObjects.model.Request import Request

		httpMessage = parseMIMEmessage(content)	
		msgString = httpMessage.getMainPart()
		if isinstance(httpMessage, HttpMessage): # multipart
			Tools.messagePartsForParse = httpMessage.getNonMainPartsAsDict() 
			
		else: # single part
			print '** No encryption here. Single part! **'
			Tools.messagePartsForParse = {}
				
		# convert msgString to Response or Request object		
		model = cls.fromString(msgString, SERIALIZATION.TURTLE)   		
		msgResource = cls.getResourceByType(RESOURCE.REQUEST, model)	
		# This step might consume items from Tools.messagePartsForParse
		return Request.parse(msgResource)
	
	@classmethod	
	def parseResponse(cls, content):
		'''
		Same as parseRequest() method, but returns a Response Object. It is supposed
		to use after serializeResponse() call.
		'''
		from SeasObjects.model.Response import Response
		
		httpMessage = parseMIMEmessage(content)	
		msgString = httpMessage.getMainPart()
		if isinstance(httpMessage, HttpMessage): # multipart
			Tools.messagePartsForParse = httpMessage.getNonMainPartsAsDict() 
			
		else: # single part
			print '** No encryption here. Single part! **'
			Tools.messagePartsForParse = {}
		
		# convert msgString to Response or Request object.		
		model = cls.fromString(msgString, SERIALIZATION.TURTLE)   		
		msgResource = cls.getResourceByType(RESOURCE.RESPONSE, model)	
		# This step might consume items from Tools.messagePartsForParse
		return Response.parse(msgResource)
		
	messageParts = {} 
	''' A dictionary for keeping non-Main parts. Key is URI of a model class Object, value is
		encrypted string representation of this object.
		Every execution of serializeToReference() from Obj object or its subClass will add one 
		item to this dictionary. It will be cleared at the beginning and at the end of 
		Tools().serializeMessage() method ''' 
	@classmethod
	def saveForMessageParts(cls, uri, partString):
		'''
		This method is only used by Obj().serializeToReference() 
		'''
		cls.messageParts[uri] = partString
		
	messagePartsForParse = {} 
	''' Similar as the above 'messageParts' dictionary. 
	It will be filled with items in the middle of Tools.parseRequest() or Tools.parseResponse() method. 
	Every execution of parse() from Obj object or its subClass will consume one item from this dictionary 
	if the URI matches the key.'''
							
			