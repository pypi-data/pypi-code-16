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

class Amountdecline(BaseObject):
	"""
	
	"""

	__config = {
		
		"88c2a21d-24b4-400a-87ad-25aa775389e3" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/transactionamount", "create", [], []),
		
		"55463c87-5bf0-48e6-b424-62971cb23d9e" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/transactionamount", "delete", [], []),
		
		"b7d35abd-2f8e-4d1e-8bc7-fcd8e4f577de" : OperationConfig("/issuer/spendcontrols/v1/card/{uuid}/controls/declines/transactionamount", "query", [], []),
		
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
		Creates object of type Amountdecline

		@param Dict mapObj, containing the required parameters to create a new object
		@return Amountdecline of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("88c2a21d-24b4-400a-87ad-25aa775389e3", Amountdecline(mapObj))









	@classmethod
	def deleteById(cls,id,map=None):
		"""
		Delete object of type Amountdecline by id

		@param str id
		@return Amountdecline of the response of the deleted instance.
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

		return BaseObject.execute("55463c87-5bf0-48e6-b424-62971cb23d9e", Amountdecline(mapObj))

	def delete(self):
		"""
		Delete object of type Amountdecline

		@return Amountdecline of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("55463c87-5bf0-48e6-b424-62971cb23d9e", self)








	@classmethod
	def query(cls,criteria):
		"""
		Query objects of type Amountdecline by id and optional criteria
		@param type criteria
		@return Amountdecline object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("b7d35abd-2f8e-4d1e-8bc7-fcd8e4f577de", Amountdecline(criteria))


