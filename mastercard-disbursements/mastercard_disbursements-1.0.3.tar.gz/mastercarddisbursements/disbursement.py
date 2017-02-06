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

class Disbursement(BaseObject):
	"""
	
	"""

	__config = {
		
		"4bb14ea3-cd2a-4c94-a36f-bdce128c47d5" : OperationConfig("/send/v1/partners/{partnerId}/disbursements/{disbursementId}", "read", [], []),
		
		"e317935d-804d-4246-af41-4b6ef5a9a4ee" : OperationConfig("/send/v1/partners/{partnerId}/disbursements", "query", [], ["ref"]),
		
		"b52f950f-67e7-4f2d-8846-2c98e95822d8" : OperationConfig("/send/v1/partners/{partnerId}/disbursements/payment", "create", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUI)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig().getVersion(), ResourceConfig().getHost(), ResourceConfig().getContext())






	@classmethod
	def readByID(cls,id,criteria=None):
		"""
		Returns objects of type Disbursement by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Disbursement
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

		return BaseObject.execute("4bb14ea3-cd2a-4c94-a36f-bdce128c47d5", Disbursement(mapObj))







	@classmethod
	def readByReference(cls,criteria):
		"""
		Query objects of type Disbursement by id and optional criteria
		@param type criteria
		@return Disbursement object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("e317935d-804d-4246-af41-4b6ef5a9a4ee", Disbursement(criteria))

	@classmethod
	def create(cls,mapObj):
		"""
		Creates object of type Disbursement

		@param Dict mapObj, containing the required parameters to create a new object
		@return Disbursement of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("b52f950f-67e7-4f2d-8846-2c98e95822d8", Disbursement(mapObj))







