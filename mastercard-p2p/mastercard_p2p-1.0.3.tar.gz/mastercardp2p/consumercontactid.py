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

class ConsumerContactID(BaseObject):
	"""
	
	"""

	__config = {
		
		"9486ed36-05ed-44e9-b4e7-27de11fa1cc2" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids", "create", [], []),
		
		"84f76f48-2712-4cdd-bb64-80a3ba0c2d61" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids/{contactId}", "delete", [], []),
		
		"b2f8acd6-39ea-4415-81a8-336117602f31" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids/{contactId}", "read", [], []),
		
		"506e1378-e78a-4b6e-9d73-1de62c3282f5" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids", "query", [], []),
		
		"8376dbed-6a72-4e93-9604-b4e8a386fbd4" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/contact_ids/{contactId}", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUI)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig().getVersion(), ResourceConfig().getHost(), ResourceConfig().getContext())


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type ConsumerContactID

		@param Dict mapObj, containing the required parameters to create a new object
		@return ConsumerContactID of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("9486ed36-05ed-44e9-b4e7-27de11fa1cc2", ConsumerContactID(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type ConsumerContactID by id

		@param str id
		@return ConsumerContactID of the response of the deleted instance.
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

		return BaseObject.execute("84f76f48-2712-4cdd-bb64-80a3ba0c2d61", ConsumerContactID(mapObj))

	def delete(self):
		"""
		Delete object of type ConsumerContactID

		@return ConsumerContactID of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("84f76f48-2712-4cdd-bb64-80a3ba0c2d61", self)







	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type ConsumerContactID by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of ConsumerContactID
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

		return BaseObject.execute("b2f8acd6-39ea-4415-81a8-336117602f31", ConsumerContactID(mapObj))







	@classmethod
	def listAll(cls,criteria):
		"""
		Query objects of type ConsumerContactID by id and optional criteria
		@param type criteria
		@return ConsumerContactID object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("506e1378-e78a-4b6e-9d73-1de62c3282f5", ConsumerContactID(criteria))


	def update(self):
		"""
		Updates an object of type ConsumerContactID

		@return ConsumerContactID object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("8376dbed-6a72-4e93-9604-b4e8a386fbd4", self)






