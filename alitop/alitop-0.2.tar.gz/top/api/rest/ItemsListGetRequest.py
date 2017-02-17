'''
Created by auto_sdk on 2016.05.03
'''
from top.api.base import RestApi
class ItemsListGetRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.fields = None
		self.num_iids = None

	def getapiname(self):
		return 'taobao.items.list.get'
