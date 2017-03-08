# -*- coding: UTF-8 -*-
import json
import httplib
from datetime import datetime
import base64

class uploadTestcase():
    web = "192.168.145.20:8088"
    baseurl = "/testsite/testcasecommand"
    pid = 0;
    versionid = 0
    def __init__(self,p):
        self.pid = p
        self.versionid = self.getversion()
    def getversion(self):
        if self.pid != 0:
            url = self.baseurl + "?mothed=getversion&project=" + str(self.pid)
            conn = httplib.HTTPConnection(self.web)  
            conn.request("GET", url)
            response = conn.getresponse()
            data = response.read()
            a = MyDecoder().decode(data)
            #print a[u'name']
            return a[u'id']

    def gettestcase(self):
        url = self.baseurl + "?mothed=gettestcase&project=" + str(self.pid)
        conn = httplib.HTTPConnection(self.web)  
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
        
        a = MyDecoder().decode(data)
        #print u'第一个测试用例名称：' + a[0][u'name']
        return a[0][u'name']

    def gettestcase(self,caseid):
        url = self.baseurl + "?mothed=getonetestcase&caseid="+caseid
        conn = httplib.HTTPConnection(self.web)  
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        return a

    def uploadPic(self,path,caseid):
        body = self.getpicbase64(path)
        headers = {"Content-type": "application/text"
                    , "Accept": "text/plain"}
        url = self.baseurl + "?mothed=insertpic&verid=" + str(self.versionid) +"&caseid=" + str(caseid)
        conn = httplib.HTTPConnection(self.web)
        conn.request("POST",url=url, body=body,headers=headers)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        return a[u"message"]

    def updateTestCase(self,caseid,content):
        obj = updateCaseClass()
        obj.baseLine = 0
        obj.CaseID=caseid
        obj.url = ''
        obj.body = ''
        obj.Content = content
        obj.mothed = ''
        params = MyEncoder().encode(obj)
        print params
        headers = {"Content-type": "application/json"
                    , "Accept": "text/plain"}
        url = self.baseurl + "?mothed=updatecase&caseid=2"
        conn = httplib.HTTPConnection(self.web)
        conn.request("POST",url=url, body=params,headers=headers)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        print a[u"message"]

    def insertModeltype(self,name,res,duptime):
        obj = modeltypeClass()
        obj.Name = name
        obj.Result = res
        obj.Pid = self.pid
        obj.Time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        obj.DupTime = duptime
        params = MyEncoder().encode(obj)
        print params
        headers = {"Content-type": "application/json"
                    , "Accept": "text/plain"}
        url = self.baseurl + "?mothed=inserttypemodel"
        conn = httplib.HTTPConnection(self.web)
        conn.request("POST",url=url, body=params,headers=headers)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        print a[u"message"]
    def uploadResult(self,caseid,picurl):
        obj = testResult()
        obj.ID = 1
        obj.AssertResult = ''
        obj.verID = self.versionid
        obj.AssertStr = ''
        obj.caseID = caseid
        obj.ResultA = ''
        obj.ResultB = ''
        obj.ResultC = ''
        obj.ReturnStr = ''
        obj.UIPicture = picurl
        
        params = MyEncoder().encode(obj)
        #print params
        headers = {"Content-type": "application/json"
                    , "Accept": "text/plain"}
        url = self.baseurl + "?mothed=insertresult&project=" + str(self.pid)
        conn = httplib.HTTPConnection(self.web)
        conn.request("POST",url=url, body=params,headers=headers)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        return a[u"message"]
    def uploadResultAssertRes(self,caseid,picurl,assertresult):
        obj = testResult()
        obj.ID = 1
        obj.AssertResult = assertresult
        obj.verID = self.versionid
        obj.AssertStr = ''
        obj.caseID = caseid
        obj.ResultA = ''
        obj.ResultB = ''
        obj.ResultC = ''
        obj.ReturnStr = ''
        obj.UIPicture = picurl
        
        params = MyEncoder().encode(obj)
        #print params
        headers = {"Content-type": "application/json"
                    , "Accept": "text/plain"}
        url = self.baseurl + "?mothed=insertresult&project=" + str(self.pid)
        conn = httplib.HTTPConnection(self.web)
        conn.request("POST",url=url, body=params,headers=headers)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        return a[u"message"]

    def uploadResultContent(self,caseid,picurl,content):
        obj = testResult()
        obj.ID = 1
        obj.AssertResult = ''
        obj.verID = self.versionid
        obj.AssertStr = content
        obj.caseID = caseid
        obj.ResultA = ''
        obj.ResultB = ''
        obj.ResultC = ''
        obj.ReturnStr = ''
        obj.UIPicture = picurl
        
        params = MyEncoder().encode(obj)
        #print params
        headers = {"Content-type": "application/json"
                    , "Accept": "text/plain"}
        url = self.baseurl + "?mothed=insertresult&project=" + str(self.pid)
        conn = httplib.HTTPConnection(self.web)
        conn.request("POST",url=url, body=params,headers=headers)
        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        return a[u"message"]
    def getpicbase64(self,path):
        f=open(path,'rb')
        ls_f=base64.b64encode(f.read())
        f.close()
        return ls_f

class newTestCaseClass():
    ID = 0
    Name = ''
    Desc = ''
    order = 0.0
    Type = '';
    Pid = 0;
    Status = ''
    funCase = None
    interfaceCase = None
    UICase = None
    def __init__(self):
        funCase = funTestCase()
        interfaceCase = interfaceTestCase()
        self.UICase = uitestcase()
        pass
class funTestCase():
    Content = ''
    def __init__(self):
        pass
class interfaceTestCase():
    mothed = ''
    address = ''
    body = ''
    def __init__(self):
        pass
class uitestcase():
    baseLine = 0
    def __init__(self):
        pass
class version():
    ID = 0
    Name = ''
    Pid =0
    Desc = ''
    def __init__(self):
        pass
class testResult():
    ID = 0
    caseID = 0
    verID = 0
    AssertResult = ''
    AssertStr = ''
    UIPicture = ''
    ReturnStr = ''
    ResultA = ''
    ResultB = ''
    ResultC = ''
    def __init__(self):
        pass
class updateCaseClass():
    CaseID = 0
    Content =''
    baseLine = 0
    mothed = ''
    body = ''
    url = ''
    def __init__(self):
        pass
class modeltypeClass():
    Name = ''
    Result = ''
    Time =''
    Pid = ''
    DupTime = ''
    def __init__(self):
        pass

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


