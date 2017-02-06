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
		
		"c54a8f39-3d43-4097-a050-adcb1a4fdc0d" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}", "delete", [], []),
		
		"fab02ec4-e05d-40a5-9b00-8015b012ca0d" : OperationConfig("/send/v1/partners/{partnerId}/consumers", "create", [], []),
		
		"d45c77d8-d9e1-4d73-829d-a805b15d0d29" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}", "read", [], []),
		
		"5fd44d9e-1583-443b-9d2f-6e9f31da9378" : OperationConfig("/send/v1/partners/{partnerId}/consumers", "query", [], ["ref","contact_id_uri"]),
		
		"62df7dfc-3071-4711-b9d2-d18ae7837f14" : OperationConfig("/send/v1/partners/{partnerId}/consumers/search", "create", [], []),
		
		"1725a7b8-b96e-47f8-8872-733f425e0750" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}", "update", [], []),
		
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

		return BaseObject.execute("c54a8f39-3d43-4097-a050-adcb1a4fdc0d", Consumer(mapObj))

	def delete(self):
		"""
		Delete object of type Consumer

		@return Consumer of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("c54a8f39-3d43-4097-a050-adcb1a4fdc0d", self)



	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Consumer

		@param Dict mapObj, containing the required parameters to create a new object
		@return Consumer of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("fab02ec4-e05d-40a5-9b00-8015b012ca0d", Consumer(mapObj))










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

		return BaseObject.execute("d45c77d8-d9e1-4d73-829d-a805b15d0d29", Consumer(mapObj))







	@classmethod
	def listByReferenceOrContactID(cls,criteria):
		"""
		Query objects of type Consumer by id and optional criteria
		@param type criteria
		@return Consumer object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("5fd44d9e-1583-443b-9d2f-6e9f31da9378", Consumer(criteria))

	@classmethod
	def listByReferenceContactIDOrGovernmentID(cls,mapObj):
		"""
		Creates object of type Consumer

		@param Dict mapObj, containing the required parameters to create a new object
		@return Consumer of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("62df7dfc-3071-4711-b9d2-d18ae7837f14", Consumer(mapObj))







	def update(self):
		"""
		Updates an object of type Consumer

		@return Consumer object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("1725a7b8-b96e-47f8-8872-733f425e0750", self)






