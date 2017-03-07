import urllib.request
import json

from Cosmos.Storage import Cache
from Cosmos.Security import Encryption
from Cosmos.Exceptions import NotFoundInApiException

class Content:

    def __init__(self, cosmos, apiName):
        self._cosmos = cosmos
        self._apiName = apiName

    def __str__(self):
        return self.body()

    def fetch(self):
        cache = Cache.getInstance()

        if cache.has(self.apiName()):
            content = cache.get(self.apiName())
            self._body = content["body"]
            self._name = content["name"]
            self._type = content["type"]
            return

        try:
            res = urllib.request.urlopen(self.url()).readall().decode('utf-8')
        except urllib.error.HTTPError: raise NotFoundInApiException()

        content = json.loads(str(res))["contents"]
        self._body = Encryption.decrypt(content["body"], content["cipher"], self._cosmos)
        self._name = content["name"]
        self._type = content["type"]

        cache.addContent(self).save()

    def body(self):
        return self._body

    def name(self):
        return self._name

    def type(self):
        return self._type

    def apiName(self):
        return self._apiName

    def url(self):
        return "https://cosmos-cms.com/api/"+ self._cosmos.getApiKey() +"/"+ self.apiName()
