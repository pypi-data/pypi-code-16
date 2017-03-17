# -*- coding: UTF-8 -*- 
import json
import httplib
import base64

class User():
    UserName = ''
    Mobile = ''
    MobilePWD = ''
    DomainUser = ''
    DomainPWD = ''
    def __init__(self,userid):
        self.User = None
        http = HttpUser()
        data = http.getUser(userid)
        self.UserName = data[u'UserName']
        self.Mobile = data[u'Mobile']
        self.MobilePWD = data[u'MobilePWD']
        self.DomainUser = data[u'DomainName']
        self.DomainPWD = data[u'DomainPWD']
    def getUser(self):
        return self
    def getPWD(self,pwd):
        return base64.b64decode(str(pwd))

class Person():
    PersonName = ''
    Mobile = ''
    Road = ''
    Sex =''
    IDcard =''
    Email =''
    Status =''
    PinYin = ''
    def __init__(self):
        self.Person = None
        http = HttpPerson()
        data = http.getPerson()
        self.PersonName = data[u'Name']
        self.Mobile = data[u'Tel']
        self.Road = data[u'Road']
        self.Sex = data[u'Sex']
        self.IDcard = data[u'IDcard']
        self.Email = data[u'Email']
        self.Status = data[u'Status']
        self.PinYin = data[u'PinYin']
    def getPerson(self):
        return self

class HttpUser():
    web = "192.168.145.20:8088"
    baseurl = "/testsite/yixincommand"
    def __init__(self):
        pass
    def getUser(self,userid):
        url = self.baseurl + "?mothed=getuser&userid=" + userid
        conn = httplib.HTTPConnection(self.web)  
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        if a[u'code'] == 0:
            print a[u'data']
            return a[u'data']
        else:
            print a[u'message']
            return a[u'message']

class HttpPerson():
    web = "192.168.145.20:8088"
    baseurl = "/testsite/personinfocommand"
    def __init__(self):
        pass
    def getPerson(self):
        url = self.baseurl + "?mothed=getperson"
        conn = httplib.HTTPConnection(self.web)  
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        if a[u'code'] == 0:
            print a[u'data']
            return a[u'data']
        else:
            print a[u'message']
            return a[u'message']

class MyEncoder(json.JSONEncoder):
    def default(self,obj):
        d = {}
        d.update(obj.__dict__)
        return d
 
class MyDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self,object_hook=self.dict2object)
    def dict2object(self,d):
        #convert dict to object
        if'__class__' in d:
            module = __import__(module_name)
            class_ = getattr(module,class_name)
            args = dict((key.encode('ascii'), value) for key, value in d.items()) #get args
            inst = class_(**args) #create new instance
        else:
            inst = d
        return inst