#
# Copyright (c) 2016 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from resourceconfig import ResourceConfig

class Consumer(BaseObject):
	"""
	
	"""

	__config = {
		
		"13643d55-1753-4813-b627-9cf0c1447e9c" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}", "delete", [], []),
		
		"907e1092-b5d5-4fc5-ab93-b63650c2e191" : OperationConfig("/send/v1/partners/{partnerId}/consumers", "create", [], []),
		
		"c5408395-d460-4a5c-aa1e-c1f9e201b7c2" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}", "read", [], []),
		
		"12de6ff8-15bc-42a1-aef1-d2c0c3c7bc3e" : OperationConfig("/send/v1/partners/{partnerId}/consumers", "query", [], ["ref","contact_id_uri"]),
		
		"ecf6122b-5698-4a67-9a32-9dbc782db5c8" : OperationConfig("/send/v1/partners/{partnerId}/consumers/search", "create", [], []),
		
		"247f5b9c-6072-4e70-a946-dc9527551fc7" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUI)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig().getVersion(), ResourceConfig().getHost(), ResourceConfig().getContext())





	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type Consumer by id

		@param str id
		@return Consumer of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""

		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if map:
			if (isinstance(map,RequestMap)):
				mapObj.setAll(map.getObject())
			else:
				mapObj.setAll(map)

		return BaseObject.execute("13643d55-1753-4813-b627-9cf0c1447e9c", Consumer(mapObj))

	def delete(self):
		"""
		Delete object of type Consumer

		@return Consumer of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("13643d55-1753-4813-b627-9cf0c1447e9c", self)



	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Consumer

		@param Dict mapObj, containing the required parameters to create a new object
		@return Consumer of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("907e1092-b5d5-4fc5-ab93-b63650c2e191", Consumer(mapObj))










	@classmethod
	def readByID(cls,id,criteria=None):
		"""
		Returns objects of type Consumer by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Consumer
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("c5408395-d460-4a5c-aa1e-c1f9e201b7c2", Consumer(mapObj))







	@classmethod
	def listByReferenceOrContactID(cls,criteria):
		"""
		Query objects of type Consumer by id and optional criteria
		@param type criteria
		@return Consumer object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("12de6ff8-15bc-42a1-aef1-d2c0c3c7bc3e", Consumer(criteria))

	@classmethod
	def listByReferenceContactIDOrGovernmentID(cls,mapObj):
		"""
		Creates object of type Consumer

		@param Dict mapObj, containing the required parameters to create a new object
		@return Consumer of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("ecf6122b-5698-4a67-9a32-9dbc782db5c8", Consumer(mapObj))







	def update(self):
		"""
		Updates an object of type Consumer

		@return Consumer object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("247f5b9c-6072-4e70-a946-dc9527551fc7", self)






