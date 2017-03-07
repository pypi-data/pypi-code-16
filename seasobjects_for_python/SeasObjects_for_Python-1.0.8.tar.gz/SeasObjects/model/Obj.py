
import datetime
import traceback

from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.PROPERTY import PROPERTY
from SeasObjects.common.Tools import Tools
from SeasObjects.rdf.Resource import Resource
from SeasObjects.rdf.Statement import Statement
from SeasObjects.common.SERIALIZATION import SERIALIZATION
from SeasObjects.common.SeasCrypto import SeasCrypto

from rdflib.term import Literal, BNode
from rdflib import URIRef
import uuid
import hashlib
import base64

class Obj(object):
		
	referenceUriPrefix = "http://smarteg.org/reference/1.0/seas#"
	ConceptDetailsEngine = None
	
	def __init__(self, seasIdentifierUri = None):
		self.seasIdentifierUri = seasIdentifierUri
		self.sameAs = None
		self.name = None
		self.generatedBy = None
		self.generatedAt = None
		self.description = None
		self.types = []
		self.provenances = []
		self.targets = []

		# map for properties (name, propertyobject pairs)
		self.properties = {}
		
		self.offerings = []
		
		# Reference object related properties
		# the following all String
		self.signature = None
		self.sessionKey = None
		self.hashCode = None
		# the following all Obj
		self.encryptionKeyType = None
		self.notary = None
		
		self.serializeAsReference = False	
		self.encrypted = False	
		self.signed = False
		# keys		
		self.encryptKey = None	#  it is also public key
		self.privateKey = None # i.e., signKey in Obj.java			
		# if the Obj is a reference, then encryptedStringRepresentation will have a String value after parse()
		self.encryptedStringRepresentation = None
		# only needed for NOTARIZEDSESSIONKEY type
		self.senderId = ""
				

	def _convert(self, obj, model):
		if isinstance(obj, Obj):
			return obj.serialize(model)
		elif isinstance(obj, URIRef):
			return obj
		else:
			return Literal(obj)
	
	def serialize(self, model):
		'''
		turn current Object into a rdf Resource
		'''
		if self.serializeAsReference:
			return self.serializeToReference(model)
		
		# create resource
		if self.hasSeasIdentifierUri():
			resource = model.createResource( self.seasIdentifierUri )
		else:
			resource = model.createResource()
		
		# sameas
		if self.hasSameAs():
			#sameAsRes = model.createResource(self.sameAs)
			owlSameAs = model.createProperty( PROPERTY.SAMEAS )
			resource.addProperty( owlSameAs, self.sameAs.serialize(model) )
		
		# generatedby
		if self.hasGeneratedBy():
			resource.addProperty( model.createProperty( PROPERTY.GENERATEDBY ), self.generatedBy.serialize(model) )
		
		# generatedat
		if self.hasGeneratedAt():
			resource.addProperty(model.createProperty( PROPERTY.GENERATEDAT ), model.createLiteral(self.getGeneratedAt()))

		
		# types
		typeProp = model.createProperty( PROPERTY.RDF_TYPE )
		for type in self.types:
			try:
				serialized = type.serialize(model)
			except:
				serialized = URIRef(type)
			resource.addProperty( typeProp, serialized )
			
		# targets
		for target in self.targets:
			resource.addProperty(model.createProperty( PROPERTY.TARGET ), model.createResource(target))
		
		# provenances
		provenanceProp = model.createProperty( PROPERTY.PROVENANCE )
		for p in self.provenances:
			resource.addProperty( provenanceProp, p.serialize(model) )
		
		# set offerings
		for offering in self.offerings:
			resource.addProperty(model.createProperty( PROPERTY.OFFERS ), offering.serialize(model))
				
		# name
		if self.hasName():
			rdfsLabel = model.createProperty( PROPERTY.RDFS_LABEL )
			resource.addProperty( rdfsLabel, self.name )
						
		# comment
		if self.hasDescription():
			rdfsComment = model.createProperty( PROPERTY.COMMENT )
			resource.addProperty( rdfsComment, self.description )
		
		# Usually the following five properties should have None value. But they can have value if this
		# Obj is recovered from a reference.
		#sessionKey
		if self.hasSessionKey():
			resource.addProperty(model.createProperty( PROPERTY.SESSIONKEY), model.createLiteral(self.sessionKey) )
		#signature
		if self.hasSignature():
			resource.addProperty(model.createProperty( PROPERTY.SIGNATURE), model.createLiteral(self.signature) )
		# hashcode
		if self.hasHashCode():
			resource.addProperty(model.createProperty( PROPERTY.HASHCODE), model.createLiteral(self.hashCode))
		# encryptionKeyType
		if self.hasEncryptionKeyType():
			resource.addProperty(model.createProperty(PROPERTY.ENCRYPTIONKEYTYPE), model.createResource(self.getEncryptionKeyType()))
		# notary
		if self.hasNotary():
			resource.addProperty(model.createProperty(PROPERTY.NOTARY), model.createResource(self.getNotary()))											
			
		# add object properties
		for key, entry in self.properties.iteritems():
			if isinstance(entry, list):
				for e in entry:
					self._add_property(resource, key, e, model)
			else:
				self._add_property(resource, key, entry, model)

		return resource;

	def serializeToReference(self, model):
		'''
		serialize to an encrypted version of this Object. Its actual content is saved in Tools.messageParts
				
		@return: a rdf Resource				
		'''
		from SeasObjects.agents.TransactionAgent import TransactionAgent
				
		print "serialize  as a Reference ..."
		
		# generate a SeasIdentifierUri for this object if not yet exist. Anonymous is not allowed here.
		if (self.hasSeasIdentifierUri() == False):
			self.setSeasIdentifierUri(self.referenceUriPrefix + str(uuid.uuid4()))
		
		# convert current Object to string for later encryption
		self.serializeAsReference=False
		partString = Tools().toString(self, SERIALIZATION.TURTLE)
		
		# using the string to generate encrypted string
		crypto = SeasCrypto()
		if self.encrypted:
			#	 encrypting the normally serialized Object
			# symmetric with notary
			if self.getEncryptionKeyType()== RESOURCE.NOTARIZEDSESSIONKEY:
				sessionkey = crypto.generateSymmetricKey()							
				partString = crypto.symmetricEncrypt(sessionkey, partString)			
				# encrypt session key with recipient's public key
				encryptedKey = crypto.encryptAndEncodeKey(self.encryptKey, sessionkey)
				# calculate hashcode
				hash = crypto.createEncodedMessageDigest(partString)
				self.setHashCode(hash)
				
				if self.signed:
					signature = crypto.sign(self.privateKey, self.getHashCode())
					self.setSignature(signature)
				
				# send encryptedKey to notary for storing						
				if  not TransactionAgent.sendKeyToNotary(self.senderId, self.getSeasIdentifierUri(),
						hash, encryptedKey, self.getSignature(), self.getNotary()) :
					print "Sending notarized session key to notary failed."				
					
			# with public key
			if self.getEncryptionKeyType()==RESOURCE.PUBLICKEY:
				# encrypt data with encrypted session key attached  			
				partString = crypto.asymmetricEncrypt(self.encryptKey, partString)[0]
						
			# with only session key. *insecure*
			if self.getEncryptionKeyType()==RESOURCE.SESSIONKEY:
				# encrypt data		
				partString = crypto.symmetricEncrypt(self.encryptKey, partString)		
				#	save key to reference
				sessionkeyAsString = base64.b64encode(self.encryptKey)
				self.setSessionKey(sessionkeyAsString)
				
		if not self.hasHashCode():
			hash = crypto.createEncodedMessageDigest(partString)
			self.setHashCode(hash)
			
		if self.signed and (not self.hasSignature()):				
				signature = crypto.sign(self.privateKey, self.getHashCode())
				self.setSignature(signature)
							
		# save encrypted or unencrypted partString and its uri to multipart as body part
		Tools.saveForMessageParts(self.getSeasIdentifierUri(), partString)
		
		# add all these to the new Resource
		# Note: MULTIPARTREFERENCE type is not included in encrypted string representation.  
		self.addType(RESOURCE.MULTIPARTREFERENCE)
		resource = model.createResource(self.getSeasIdentifierUri())
		#	type
		typeProp = model.createProperty( PROPERTY.RDF_TYPE )
		for type in self.types:
			try:
				serialized = type.serialize(model)
			except:
				serialized = URIRef(type)
			resource.addProperty( typeProp, serialized )		
		#sessionKey
		if self.hasSessionKey():
			resource.addProperty(model.createProperty( PROPERTY.SESSIONKEY), model.createLiteral(self.sessionKey) )
		#signature
		if self.hasSignature():
			resource.addProperty(model.createProperty( PROPERTY.SIGNATURE), model.createLiteral(self.signature) )
		# hashcode
		if self.hasHashCode():
			resource.addProperty(model.createProperty( PROPERTY.HASHCODE), model.createLiteral(self.hashCode))
		# encryptionKeyType
		if self.hasEncryptionKeyType():
			resource.addProperty(model.createProperty(PROPERTY.ENCRYPTIONKEYTYPE), model.createResource(self.getEncryptionKeyType()))
		# notary
		if self.hasNotary():
			resource.addProperty(model.createProperty(PROPERTY.NOTARY), model.createResource(self.getNotary()))
							
		return resource
	
	def getStringRepresentation(self):
		return self.encryptedStringRepresentation		

	def _add_property(self, resource, property, entry, model):
		from SeasObjects.model.Parameter import Parameter
		
		if not isinstance(property, URIRef):
			obj = Parameter(key = property, value = entry)
			property = PROPERTY.PARAMETER
		else:
			obj = entry
		resource.addProperty( model.createProperty( property ), self._convert(obj, model))
	
	@classmethod
	def parse(cls, element):
		'''
		factory method and class method. It takes in Resource as parameter, create a Seas Obj or 
		its subClass object. 
		
		@return: this newly created object, which could be either a real Obj or its subclass Object 
		or a Reference, whose actual content is in multipart message's body part  
		'''
		if isinstance(element, Resource):
			if not element.isAnon():
				obj = cls(element.toString())
			else:
				obj = cls()
			
			for i in element.findProperties():
				obj.parseStatement(i)
			
			# check whether this Obj is a reference
			if obj.isOfType(RESOURCE.MULTIPARTREFERENCE):
				if obj.hasSeasIdentifierUri():
					#print '***** ', obj.getSeasIdentifierUri(), ' is a reference **** '
					if (len(Tools.messagePartsForParse)>0) and (obj.getSeasIdentifierUri() in Tools.messagePartsForParse):						
						stringRepresentation = Tools.messagePartsForParse[obj.getSeasIdentifierUri()]
						#print '******', obj.getSeasIdentifierUri(), ' has its actual content saved in String:\n ', stringRepresentation, '\n******'
						# if this Obj is EncryptedReference, it will be decrypted later by decrypt() call.
						if obj.isOfType(RESOURCE.ENCRYPTEDREFERENCE):						
							obj.encryptedStringRepresentation = stringRepresentation
						else: # if not encrypted, replace this reference Obj with a new Object, 
							# which is deserialzed from the stringRepresentation, containing actual content.
							# This happens in the case of digital signature  
							#print 'replacing reference Obj with actual Object recovered from string representation....'
							model = Tools().fromString(stringRepresentation, SERIALIZATION.TURTLE)
							# find the root Resource
							rootRes = Tools().getTopNode(model)[0]
							# figure out its SEAS Class
							seasCls = Tools().getResourceClass(rootRes)
							# recover it to Obj or its subclass Object
							recoveredObj =  seasCls.parse(rootRes)
							# copy signature, hashcode from reference Obj to recovered Obj
							recoveredObj.setSignature(obj.getSignature()) 
							recoveredObj.setHashCode(obj.getHashCode())
							
							recoveredObj.types.remove(URIRef(RESOURCE.REFERENCE))
							obj = recoveredObj
							
						del Tools.messagePartsForParse[obj.getSeasIdentifierUri()]
					else:
						print '******* ERROR: can not find the encrypted string representation of ', obj.getSeasIdentifierUri()						
						#try:
						#	raise Exception('just to check!!!')		
						#except:
						#	traceback.print_stack()
				else:
					print '***** ERROR: reference Obj has to be named!!!*******'						
											
			return obj
		
		return None
			
	def parseStatement(self, statement):
		'''
		It takes in statement as input, add property to existing model Class object.
		Return None
		'''
		from SeasObjects.model.Parameter import Parameter
		from SeasObjects.model.Provenance import Provenance
		from SeasObjects.model.Activity import Activity
		from SeasObjects.model.Offering import Offering

		# get predicate and object
		predicate = str(statement.getPredicate())
		objectNode = statement.getObject()
		
		# type
		if predicate == PROPERTY.RDF_TYPE:
			try:
				self.addType(URIRef(statement.getResource().toString()))
			except:
				print "Unable to interpret rdf:type value as resource."
				traceback.print_exc()
			return

		# sameas
		if predicate == PROPERTY.SAMEAS:			
			try:
				self.setSameAs(statement.getResource().toString())				
			except:
				print"Unable to interpret owl:sameAs value as resource."
				traceback.print_exc()
			return

		# generatedby
		if predicate == PROPERTY.GENERATEDBY:
			try:
				self.setGeneratedBy(Activity.parse(statement.getResource()))
			except:
				print "Unable to interpret seas:generatedBy value as resource."
				traceback.print_exc()
			return
		
		# generatedat
		if predicate == PROPERTY.GENERATEDAT:
			try:
				self.setGeneratedAt(statement.getObject().toPython())
			except:
				print "Unable to interpret seas:generatedAt value as date literal."
				traceback.print_exc()
			return

		# provenance
		if predicate == PROPERTY.PROVENANCE:
			try:
				self.addProvenance(Provenance.parse(statement.getResource()))
			except:
				print "Unable to interpret seas:provenance value as resource."
				traceback.print_exc() 
			return
		
		# offerings
		if  predicate == PROPERTY.OFFERS:
			try:
				self.addOffering(Offering.parse(statement.getResource()))
			except:
				print "Unable to interpret gr:offers value as resource."
				traceback.print_exc() 			
			return		

		# target
		if predicate == PROPERTY.TARGET:
			try:
				self.addTarget(statement.getString())
			except:
				print"Unable to interpret seas:target value as literal string."
				traceback.print_exc()
			return
		
		# label
		if predicate == PROPERTY.RDFS_LABEL:
			try:
				self.setName(statement.getString())
			except:
				print"Unable to interpret rdfs:label value as literal string."
				traceback.print_exc()
			return

		# comment
		if predicate == PROPERTY.COMMENT:
			try:
				self.setDescription(statement.getString())
			except:
				print"Unable to interpret rdfs:comment value as literal string."
				traceback.print_exc()
			return
		
		# sessionKey
		if predicate == PROPERTY.SESSIONKEY:
			try:
				self.setSessionKey(statement.getString())
			except:
				print "Unable to interpret seas:sessionKey value as literal string."
				traceback.print_exc()
			return
		# signature
		if predicate == PROPERTY.SIGNATURE:
			try:
				self.setSignature(statement.getString())
			except:
				print "Unable to interpret seas:signature value as literal string."
				traceback.print_exc()
			return
		# hashcode
		if predicate == PROPERTY.HASHCODE:
			try:
				self.setHashCode(statement.getString())
			except:
				print "Unable to interpret seas:hashCode value as literal string."
				traceback.print_exc()
			return
		# encryptionKeyType
		if predicate == PROPERTY.ENCRYPTIONKEYTYPE:
			try:
				self.setEncryptionKeyType(statement.getResource().toString())
			except:
				print "Unable to interpret seas:encryptionKeyType value as resource."
				traceback.print_exc()
			return
		# notary
		if predicate == PROPERTY.NOTARY:
			try:
				self.setNotary(statement.getResource().toString())
			except:
				print "Unable to interpret seas:notary value as resource."
				traceback.print_exc()
			return
		
		# parameters
		if predicate == PROPERTY.PARAMETER:
			p = Parameter().parse(statement.getResource())
			self.add(p.getKey(), p.getValues())
			return 
		
		# if literal object
		if isinstance(objectNode, Literal):
			self.add(URIRef(predicate), objectNode.toPython())
			return
		
		if isinstance(objectNode, URIRef):
			self.add(URIRef(predicate), objectNode)
			return

		# if resource
		if isinstance(objectNode, Resource):
			resource = statement.getResource()
			
			# first check if resource has a type implemented built-in
			# and parse using that
			klass = Tools().getResourceClass(resource, default = Obj)

			if klass is not None:
				self.add(URIRef(predicate), klass.parse(resource))
			else:
				# None found, resort to Obj (the base class)
				self.add(URIRef(predicate), Obj.parse(resource));
			
			return	
		
		# Nothing else matches, use BNode as blank default entry
		if isinstance(objectNode, BNode):
			try:
				klass = Tools().getResourceClass(statement.getResource(), default = None)
			except:
				klass = None
			if klass is not None:
				self.add(URIRef(predicate), klass.parse(statement.getResource()))
			else:
				self.add(URIRef(predicate), objectNode.toPython())
			return	
		
	
	def sign(self, key):
		'''
		the actual signature creation will be delayed until serialize, in the same way as enctype() method.
		'''
		self.signed = True
		self.privateKey = key
		self.serializeAsReference = True
		self.addType(RESOURCE.REFERENCE)
		
	def encrypt(self, key):
		'''
		Encrypt with SessionKey
		
		It just marks "serializeAsReference" to True and add additional Types, not really do any encryption.
		Encryption will be conducted during serialization.
		
		@Note: This method should not be used as it will encrypt the object with symmetric key and send that 
		key as plain text within the reference
		@return None		
		'''	
		self.encrypted = True
		self.encryptKey = key	
		self.addType(RESOURCE.REFERENCE)
		self.addType(RESOURCE.ENCRYPTEDREFERENCE)
		self.setEncryptionKeyType(RESOURCE.SESSIONKEY)
		# this is the key part
		self.serializeAsReference = True
	
	def encryptAndNotarize(self, notaryAddress, pubKey, senderID='http://unknown.seas.partner'):			
		self.encrypted = True
		self.encryptKey = pubKey
		self.addType(RESOURCE.REFERENCE)
		self.addType(RESOURCE.ENCRYPTEDREFERENCE)
		self.setNotary(notaryAddress)
		self.setEncryptionKeyType(RESOURCE.NOTARIZEDSESSIONKEY)
		self.serializeAsReference = True
		self.senderId = senderID
	
	def decrypt(self, secretKey):
		'''
		Decrypt with SessionKey.
		
		Using encrypted string to recover the original Object.
		@return a new Obj decrypted from cipertext, without those additional types like EncryptedReference and Reference, which
		were inserted by encrypt() method before.    
		'''		
		
		if self.encryptedStringRepresentation is not None:
			decryptedString = SeasCrypto().symmetricDecrypt(secretKey, self.encryptedStringRepresentation)
			
			#print '\n ******* decrypted String representation ************'
			#print decryptedString
			#print '**************************\n' 
			model = Tools().fromString(decryptedString, SERIALIZATION.TURTLE)
			# find the resource which was encrypted
			rootRes = Tools().getTopNode(model)[0]
			# figure out its SEAS Class
			seasCls = Tools().getResourceClass(rootRes)
			# recover it to Obj or its subclass Object
			recoveredObj =  seasCls.parse(rootRes)
			# remove EncryptedReference and Reference types.
			recoveredObj.types.remove(URIRef(RESOURCE.ENCRYPTEDREFERENCE))
			recoveredObj.types.remove(URIRef(RESOURCE.REFERENCE))
		
			return recoveredObj
		else:
			print '**** nothing to decrypt! *****'
	
	def verifySignature(self, publickey):	
		if (not self.hasHashCode()) or (not self.hasSignature()):
			print 'ERROR: hashcode or signature is empty!'
			return False
		else:
			return SeasCrypto().verifySignature(self.getSignature(), publickey, self.getHashCode())		
	
			
	def toNude(self):
		return self.toString()
	
	def fromNude(self):
		pass

	def getId(self):
		return self.toString()
	
	def toString(self):
		return str(self.getSeasIdentifierUri())
	
	def hasSeasIdentifierUri(self):
		# empty string is not allowed
		return (self.seasIdentifierUri is not None and self.seasIdentifierUri != "")

	def setSeasIdentifierUri(self, uri):
		self.seasIdentifierUri = uri

	def getSeasIdentifierUri(self):
		return self.seasIdentifierUri

	def hasSameAs(self):
		# empty string is not allowed
		return self.sameAs is not None

	def setSameAs(self, uri):
		'''
		@param uri: the uri string used for constructing sameAs Object
		@attention: the sameAs is changed from String type to Obj type 
		'''
		e = Obj(uri)
		e.clearTypes()
		self.sameAs = e

	def getSameAs(self):
		return self.sameAs
	
	def hasTarget(self):
		return len(self.targets) > 0
	
	def firstTarget(self):
		if self.hasTarget(): return self.targets[0]
		return None
	
	def getTargets(self):
		return self.targets
	
	def addTarget(self, t):
		self.targets.append(t)
		
	def isOfType(self, type):
		if not isinstance(type, URIRef):
			type = URIRef(type)
		return type in self.types
	
	def hasType(self):
		'''
		whether this Object has Type at all
		'''
		return len(self.types) > 0

	def clearTypes(self):
		self.types = []
		
	def setType(self, type):
		self.types = [type]
	
	def addType(self, type):		
		self.types.append(type)

	def getTypes(self):
		return self.types

	def hasName(self):
		return self.name is not None
	
	def setName(self, name):
		self.name = name
	
	def getName(self):
		return self.name

	def hasDescription(self):
		return self.description is not None
	
	def setDescription(self, description):
		self.description = description
	
	def getDescription(self):
		return self.description

	def hasProvenance(self):
		return len(self.provenances) > 0

	def getProvenances(self):
		return self.provenances

	def addProvenance(self, p):
		self.provenances.append(p)
		
	def hasOffering(self):	
		return len(self.offerings) > 0
		
	def getOfferings(self):	
		return self.offerings
		
	def setOfferings(self, offerings):	
		'''
		@param offerings: a list of Offering Objects 
		'''
		self.offerings = offerings
		
	def addOffering(self, offering):	
		self.offerings.append(offering)
		
	def hasGeneratedAt(self):
		return self.generatedAt is not None
	
	def getGeneratedAt(self):
		return self.generatedAt

	def setGeneratedAt(self, generatedAt):
		self.generatedAt = generatedAt
	
	def hasGeneratedBy(self):
		return self.generatedBy is not None

	def setGeneratedBy(self, generatedBy):
		from SeasObjects.model.Activity import Activity
		
		if isinstance(generatedBy, Activity):
			self.generatedBy = generatedBy
		elif isinstance(generatedBy, str):
			generator = Activity(generatedBy)
			self.generatedBy = generator

	def getGeneratedBy(self):
		if not self.hasGeneratedBy():
			from SeasObjects.model.Activity import Activity
			self.generatedBy = Activity()
		return self.generatedBy
		
	def listProperties(self):
		return self.getProperties().values()
	
	def hasProperties(self):
		return len(self.properties) > 0
	
	def getProperties(self):
		from SeasObjects.rdf.Variant import Variant
		map = {}
		
		for key, value in self.properties.iteritems():
			for e in value:
				# if a key does not exist yet, create new entry
				if not map.has_key(key):
					map[key] = []

				# add to arraylist
				map[key].append(Variant(e))

		return map

	def hasSessionKey(self):
		return self.sessionKey is not None

	def getSessionKey(self):
		return self.sessionKey
	
	def setSessionKey(self, sessionKey):
		self.sessionKey = sessionKey
		
	def hasSignature(self):
		return self.signature is not None
	
	def getSignature(self):
		return self.signature
	
	def setSignature(self, signature):
		self.signature = signature

	def hasHashCode(self):
		return self.hashCode is not None
	
	def getHashCode(self):
		return self.hashCode
	
	def setHashCode(self, hashCode):
		self.hashCode = hashCode
		
	def hasEncryptionKeyType(self):
		return self.encryptionKeyType is not None
	
	def getEncryptionKeyType(self):
		'''
		@return: URI of Object
		'''
		if self.encryptionKeyType is not None:
			return self.encryptionKeyType.getSeasIdentifierUri()
		
	def setEncryptionKeyType(self, encryptionKeyTypeUri):	
		'''
		@type encryptionKeyTypeUri: a URI string
		'''
		o = Obj(encryptionKeyTypeUri)
		o.clearTypes()
		self.encryptionKeyType = o
		
	def hasNotary(self):
		return self.notary is not None
	
	def getNotary(self):
		'''
		@return: URI of Object
		'''
		if self.notary is not None:
			return self.notary.getSeasIdentifierUri()
		
	def setNotary(self, notaryUri):
		'''
		@type notaryUri: a URI string
		'''
		o = Obj(notaryUri)
		o.clearTypes()
		self.notary = o

	def get(self, property):
		from SeasObjects.rdf.Variant import Variant
		ret = []
		
		if self.properties.has_key(property):
			for e in self.properties[property]:
				if isinstance(e, Variant):
					ret.append(e)
				else:
					ret.append(Variant(e))
		
		return ret
	
	def getFirst(self, property):
		try:
			return self.get(property)[0]
		except:
			return None
		
	def getFirstValue(self, property):
		try:
			return self.getFirst(property).getValue();
		except:
			return None
		
	def add(self, property, obj):
		if not self.properties.has_key(property):
			self.properties[property] = []
		
		self.properties[property].append(obj)

	def remove(self, property, obj):
		if self.properties.has_key(property):
			del self.properties[property]
			
	def isEncrypted(self):	
		return self.isOfType(RESOURCE.ENCRYPTEDREFERENCE)
	
	def turtlePrint(self):
		print Tools.toString(self)

	def treePrint(self, res, indentString):
		'''
		Used by explain() method for printing inner structure of a Resource.
		
		@type res: rdflib.resource.Resource		
		'''
		from rdflib import resource, URIRef, RDF, Literal 
		from SeasObjects.common.ConceptDetails import ConceptDetails
								
		if res.value(RDF.type) is None:
			return
		
		#print indentString, res.value(RDF.type).qname(), self.ConceptDetailsEngine.getComments(res.value(RDF.type).identifier)
		
		if len(self.ConceptDetailsEngine.getComments(res.value(RDF.type).identifier))>4:		
			print indentString, self.ConceptDetailsEngine.getComments(res.value(RDF.type).identifier)
		else:
			print indentString, res.value(RDF.type).qname()
								
		for p, o in res.predicate_objects():
			if p.identifier == RDF.type:
				continue
			#print indentString, ' ->', p.qname(), self.ConceptDetailsEngine.getComments(p.identifier)
			if len(self.ConceptDetailsEngine.getComments(p.identifier))>4:				
				print indentString, ' ->', self.ConceptDetailsEngine.getComments(p.identifier),
			else:
				print indentString, ' ->', p.qname(),
				
			if isinstance(o, resource.Resource):	
				print							
				# get its type and print
				self.treePrint(o,'	'+indentString)	
			else:
				print ':	',o
							
	
	def explain(self):
		from rdflib import Graph, resource, URIRef, RDF, Literal 
		from sets import Set
		from SeasObjects.common.NS import NS
		from SeasObjects.common.ConceptDetails import ConceptDetails
		
		# get the underlying rdf graph
		st = Tools.toString(self, 'text/turtle')		
		g = Graph()		
		g.parse(data=st, format='turtle' )	
		g.bind('seas', NS.SEAS)
		g.bind('geo', NS.GEO)
		g.bind('unit', NS.UNIT)
		g.bind('quantity', NS.QUANTITY)
		g.bind('owl', NS.OWL)
		
		# get the root resource
		root = resource.Resource(g, URIRef(self.getSeasIdentifierUri()))
		indent = ''
		
		if self.ConceptDetailsEngine is None:
			self.ConceptDetailsEngine = ConceptDetails()
		
		self.treePrint(root, indent)
		
		self.ConceptDetailsEngine.close()
									
		# get all the types
		#types = Set()
		#for s, o in g.subject_objects(RDF.type):
		#	types.add(o)
		
		# get all reasources - URIRef or Bnode			
		#for s, o in g.subject_objects(RDF.type):						
		#	print 'Resource: %s is type of [%s]'%(s, o)	
		#	print '	', type(s),'...', unicode(s)	
		
		# using these information to create new resources
		
		# need to replace [] or instance URLs with type URLs
			
		# delete all (s, RDF.type, o) triples, replace all resource id with its type url
		#g.remove((None, RDF.type, None))
		#new_g = Graph()
		#for s, p, o in g:
		#	if resources.has_key(s):
		#		new_g.add((resources[s], p, o))
		#	else:
		#		new_g.add((s, p, o))
		
		#print '----here is new graph----- '
		#print (new_g.serialize(format='turtle'))	
		
		
		