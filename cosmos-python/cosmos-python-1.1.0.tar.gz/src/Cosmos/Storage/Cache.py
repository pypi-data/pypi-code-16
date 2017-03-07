import os
import json
import time

class Cache:

    instance = None;

    def __init__(self, cachePath):
        self.dir = cachePath
        self.file = None
        self.refreshRate = 24*60*60
        self.contents = {}

        if(not os.path.isdir(self.dir)):
            os.mkdir(self.dir)

        dir = os.listdir(self.dir)
        self.file = dir[0] if len(dir) else ""

        if(os.path.isfile(os.path.join(self.dir, self.file))):
            cacheFile = open(os.path.join(self.dir, self.file), "r")
            self.contents = json.loads(cacheFile.read())
            cacheFile.close()

    def addContent(self, content):
        c = {}
        c["body"] = content.body()
        c["name"] = content.name()
        c["type"] = content.type()
        c["time"] = int(time.time())

        self.contents[content.apiName()] = c
        return self


    def has(self, apiName):
        if(apiName in self.contents and time.time() - self.contents[apiName]["time"] > self.refreshRate):
            return False
        return apiName in self.contents

    def get(self, apiName):
        return self.contents[apiName]

    def save(self):
        for file in os.listdir(self.dir):
            filePath = os.path.join(self.dir, file)
            os.unlink(filePath)

        cacheFile = open(os.path.join(self.dir, str(int(time.time()))), "w+")
        cacheFile.write(json.dumps(self.contents))
        cacheFile.close()

    def setRefreshRate(self, refreshRate):
        self.refreshRate = refreshRate

    @staticmethod
    def getInstance(cachePath = None):
        if(cachePath is None):
            return Cache.instance

        Cache.instance = Cache(cachePath)
        return Cache.instance
