#coding:utf-8

class DotableDict(dict):
    def __init__(self,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.__dict__ = self

    def __getattr__ (self,key):
        try:
            return self.__dict__[key]
        except:
            return ""

class JsonConfig(object):
        def __init__(self,type,value):
            self.type = type
            self.value = value

        def getType(self):
            return self.type

        def getValue(self):
            return self.value