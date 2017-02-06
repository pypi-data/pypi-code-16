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

class Crossborder(BaseObject):
	"""
	
	"""

	__config = {
		
		"468573c5-fd1b-46e1-a243-e9cdcd204722" : OperationConfig("/issuer/v1/card/{uuid}/controls/alerts/crossborder", "delete", [], []),
		
		"7a5510b8-aeb6-48b9-aad4-7ff8a87d4390" : OperationConfig("/issuer/v1/card/{uuid}/controls/alerts/crossborder", "query", [], []),
		
		"bcc0c379-6b83-4166-ae70-f4228c84cc0e" : OperationConfig("/issuer/v1/card/{uuid}/controls/alerts/crossborder", "create", [], []),
		
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
		Delete object of type Crossborder by id

		@param str id
		@return Crossborder of the response of the deleted instance.
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

		return BaseObject.execute("468573c5-fd1b-46e1-a243-e9cdcd204722", Crossborder(mapObj))

	def delete(self):
		"""
		Delete object of type Crossborder

		@return Crossborder of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("468573c5-fd1b-46e1-a243-e9cdcd204722", self)








	@classmethod
	def query(cls,criteria):
		"""
		Query objects of type Crossborder by id and optional criteria
		@param type criteria
		@return Crossborder object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("7a5510b8-aeb6-48b9-aad4-7ff8a87d4390", Crossborder(criteria))

	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Crossborder

		@param Dict mapObj, containing the required parameters to create a new object
		@return Crossborder of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("bcc0c379-6b83-4166-ae70-f4228c84cc0e", Crossborder(mapObj))







