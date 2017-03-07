import os

from Cosmos.Storage import Cache
from Cosmos.Exceptions import *
from Cosmos.Content import Content

class Cosmos():

    def __init__(self, apiKey = None):

        self.apiKey = apiKey
        self.privateKey = None
        self.contents = {}

    def setApiKey(self, apiKey):
        self.apiKey = apiKey

    def getApiKey(self):
        return self.apiKey

    def setPrivateKey(self, privateKey):
        if(os.path.isfile(privateKey)):
            keyFile = open(privateKey, "rb")
            self.privateKey = keyFile.read()
            keyFile.close()
            return
        self.privateKey = privateKey

    def getPrivateKey(self):
        return self.privateKey

    def setCachePath(self, cachePath):
        Cache.getInstance(cachePath)

    def saveCache(self):
        Cache.getInstance().save()

    def setRefreshRate(self, refreshRate):
        Cache.getInstance().setRefreshRate(refreshRate)

    def get(self, apiName):
        if self.apiKey is None:
            raise NoApiKeyException()
        if self.privateKey is None:
            raise NoPrivateKeyException()

        if apiName in self.contents:
            return self.contents[apiName]

        content = Content(self, apiName)
        content.fetch()
        self.contents[apiName] = content

        return content
