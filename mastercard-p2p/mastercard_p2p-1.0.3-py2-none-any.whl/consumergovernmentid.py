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

class ConsumerGovernmentID(BaseObject):
	"""
	
	"""

	__config = {
		
		"4cfe106e-e242-4497-99b5-c91df35f030c" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/government_ids", "create", [], []),
		
		"76588be5-140f-483e-a5be-e419ca0d61dd" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/government_ids/{governmentId}", "delete", [], []),
		
		"83376838-382b-4b20-a174-029ef2eea60a" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/government_ids/{governmentId}", "read", [], []),
		
		"a3d8f685-4e60-45ab-af49-80e7367054a6" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/government_ids", "query", [], []),
		
		"8daa3e1f-d9f4-4a77-bc25-fc173c8183ad" : OperationConfig("/send/v1/partners/{partnerId}/consumers/{consumerId}/government_ids/{governmentId}", "update", [], []),
		
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
		Creates object of type ConsumerGovernmentID

		@param Dict mapObj, containing the required parameters to create a new object
		@return ConsumerGovernmentID of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("4cfe106e-e242-4497-99b5-c91df35f030c", ConsumerGovernmentID(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type ConsumerGovernmentID by id

		@param str id
		@return ConsumerGovernmentID of the response of the deleted instance.
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

		return BaseObject.execute("76588be5-140f-483e-a5be-e419ca0d61dd", ConsumerGovernmentID(mapObj))

	def delete(self):
		"""
		Delete object of type ConsumerGovernmentID

		@return ConsumerGovernmentID of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("76588be5-140f-483e-a5be-e419ca0d61dd", self)







	@classmethod
	def read(cls,id,criteria=None):
		"""
		Returns objects of type ConsumerGovernmentID by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of ConsumerGovernmentID
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

		return BaseObject.execute("83376838-382b-4b20-a174-029ef2eea60a", ConsumerGovernmentID(mapObj))







	@classmethod
	def listAll(cls,criteria):
		"""
		Query objects of type ConsumerGovernmentID by id and optional criteria
		@param type criteria
		@return ConsumerGovernmentID object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("a3d8f685-4e60-45ab-af49-80e7367054a6", ConsumerGovernmentID(criteria))


	def update(self):
		"""
		Updates an object of type ConsumerGovernmentID

		@return ConsumerGovernmentID object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("8daa3e1f-d9f4-4a77-bc25-fc173c8183ad", self)






