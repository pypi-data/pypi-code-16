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

class PaymentTransfer(BaseObject):
	"""
	
	"""

	__config = {
		
		"3240c91a-e53b-4eb6-8c5d-e31fbfea0ed1" : OperationConfig("/send/v1/partners/{partnerId}/transfers/payment", "create", [], []),
		
		"469625f9-3f28-4f41-85a6-1aa173779de7" : OperationConfig("/send/v1/partners/{partnerId}/transfers/{transferId}", "read", [], []),
		
		"d6228a14-afd2-41da-a1e9-c2719e36a466" : OperationConfig("/send/v1/partners/{partnerId}/transfers", "query", [], ["ref"]),
		
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
		Creates object of type PaymentTransfer

		@param Dict mapObj, containing the required parameters to create a new object
		@return PaymentTransfer of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("3240c91a-e53b-4eb6-8c5d-e31fbfea0ed1", PaymentTransfer(mapObj))










	@classmethod
	def readByID(cls,id,criteria=None):
		"""
		Returns objects of type PaymentTransfer by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of PaymentTransfer
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

		return BaseObject.execute("469625f9-3f28-4f41-85a6-1aa173779de7", PaymentTransfer(mapObj))







	@classmethod
	def readByReference(cls,criteria):
		"""
		Query objects of type PaymentTransfer by id and optional criteria
		@param type criteria
		@return PaymentTransfer object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("d6228a14-afd2-41da-a1e9-c2719e36a466", PaymentTransfer(criteria))


