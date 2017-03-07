from SeasObjects.rdf.Model import Model
import traceback
import sys
import datetime

class Factory(object):

	def __init__(self):
		pass
	
	def createModel(self):
		return Model()

	def createValueObject(self, name = None, unit = None, quantity = None, description = None, datatype = None):
		from SeasObjects.model.ValueObject import ValueObject
		from SeasObjects.rdf.Variant import Variant

		vo = None
		try:
			vo = ValueObject()
			if name is not None:			vo.setName(name)
			if quantity is not None:		vo.setQuantity(quantity)
			if unit is not None:			vo.setUnit(unit)
			if description is not None:		vo.setDescription(description)
			if datatype is not None:		vo.setValue(Variant(datatype))
		except:
			print "Exception while creating a ValueObject"
			print sys.exc_info()[1]
			vo = None
		return vo
	
	"""
	 Set all namespaces declared in given class (e.g. NS) to the model.
	 @param model the model where namespaces are added
	 @param klazz class containing the namespaces as attributes
	"""
	def setNameSpaces(self, model, klazz):
		try:
			fields = klazz.getDeclaredFields();
			for field in fields:
				model.setNsPrefix(field.getName().toLowerCase(), field.get(klazz).toString())
		except:
			traceback.print_exc()
			
	@classmethod
	def createTransaction(cls, transactionIdentifierUri, generatedBy):
		'''
		return a newly generated Transaction Object 
		'''
		from SeasObjects.model.Transaction import Transaction
		from SeasObjects.model.Activity import Activity
		from SeasObjects.seasexceptions.InsufficientDataException import InsufficientDataException
		
		transaction = Transaction(transactionIdentifierUri)
		if generatedBy is None:
			raise InsufficientDataException
		
		transaction.setGeneratedBy(Activity(generatedBy))
		transaction.getGeneratedBy().clearTypes()
		
		# timestamp of when this message is being generated (now)
		transaction.setGeneratedAt(datetime.datetime.now())

		return transaction
		
		
		
