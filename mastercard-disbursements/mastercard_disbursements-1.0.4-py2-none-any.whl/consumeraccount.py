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

class ConsumerAccount(BaseObject):
	"""
	
	"""

	__config = {
		
		"b495dec8-0bab-4298-bad6-d1e9febbb4b0" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts", "create", [], []),
		
		"38c2ef31-a0a5-4089-82d1-711dc131c4ac" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts/{accountId}", "delete", [], []),
		
		"446b7238-75af-4f88-a6c9-666f8ddccc7f" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts/{accountId}", "read", [], []),
		
		"d1e68e86-c6b0-497b-8cb0-cc65abfa2940" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts", "query", [], ["ref"]),
		
		"e064a9a0-f855-49d0-b03b-ee5bef1f830e" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/accounts/{accountId}", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUI)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext())


	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type ConsumerAccount

		@param Dict mapObj, containing the required parameters to create a new object
		@return ConsumerAccount of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("b495dec8-0bab-4298-bad6-d1e9febbb4b0", ConsumerAccount(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type ConsumerAccount by id

		@param str id
		@return ConsumerAccount of the response of the deleted instance.
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

		return BaseObject.execute("38c2ef31-a0a5-4089-82d1-711dc131c4ac", ConsumerAccount(mapObj))

	def delete(self):
		"""
		Delete object of type ConsumerAccount

		@return ConsumerAccount of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("38c2ef31-a0a5-4089-82d1-711dc131c4ac", self)







	@classmethod
	def readByID(cls,id,criteria=None):
		"""
		Returns objects of type ConsumerAccount by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of ConsumerAccount
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

		return BaseObject.execute("446b7238-75af-4f88-a6c9-666f8ddccc7f", ConsumerAccount(mapObj))







	@classmethod
	def listAll(cls,criteria):
		"""
		Query objects of type ConsumerAccount by id and optional criteria
		@param type criteria
		@return ConsumerAccount object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("d1e68e86-c6b0-497b-8cb0-cc65abfa2940", ConsumerAccount(criteria))


	def update(self):
		"""
		Updates an object of type ConsumerAccount

		@return ConsumerAccount object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("e064a9a0-f855-49d0-b03b-ee5bef1f830e", self)






