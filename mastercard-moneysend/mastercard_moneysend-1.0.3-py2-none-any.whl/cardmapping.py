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

class CardMapping(BaseObject):
	"""
	
	"""

	__config = {
		
		"f6d97ee9-e3b9-4429-9b12-c9658be224a0" : OperationConfig("/moneysend/v3/mapping/card", "create", [], []),
		
		"f77efa8b-d729-47b1-84ab-daad126dbdeb" : OperationConfig("/moneysend/v3/mapping/card/{mappingId}", "delete", [], []),
		
		"a4d67113-4856-43a3-b817-9f5931f62e9a" : OperationConfig("/moneysend/v3/mapping/subscriber", "update", [], []),
		
		"52225166-44f8-449f-bd8b-d0e9ef29976e" : OperationConfig("/moneysend/v3/mapping/card", "update", [], []),
		
		"fc13311f-bed2-4e1a-938c-0c1706afccf5" : OperationConfig("/moneysend/v3/mapping/card/{mappingId}", "update", [], []),
		
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
		Creates object of type CardMapping

		@param Dict mapObj, containing the required parameters to create a new object
		@return CardMapping of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("f6d97ee9-e3b9-4429-9b12-c9658be224a0", CardMapping(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type CardMapping by id

		@param str id
		@return CardMapping of the response of the deleted instance.
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

		return BaseObject.execute("f77efa8b-d729-47b1-84ab-daad126dbdeb", CardMapping(mapObj))

	def delete(self):
		"""
		Delete object of type CardMapping

		@return CardMapping of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("f77efa8b-d729-47b1-84ab-daad126dbdeb", self)




	def deleteSubscriberID(self):
		"""
		Updates an object of type CardMapping

		@return CardMapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("a4d67113-4856-43a3-b817-9f5931f62e9a", self)






	def read(self):
		"""
		Updates an object of type CardMapping

		@return CardMapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("52225166-44f8-449f-bd8b-d0e9ef29976e", self)






	def update(self):
		"""
		Updates an object of type CardMapping

		@return CardMapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("fc13311f-bed2-4e1a-938c-0c1706afccf5", self)






