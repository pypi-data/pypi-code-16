# -*- coding: UTF-8 -*-
import os
import sys
import json
import httplib

# 传出所有的py文件
resultList = []
allFileNum = 0
overFile = "pythonTestCase.py"
projectName = u"测试用DEMO项目"

#获取当前目录下的所有py文件
def _checkPath(level, path):  
    global allFileNum
    ''''' 
    打印一个目录下的所有文件夹和文件 
    ''' 
    # 所有文件夹，第一个字段是次目录的级别  
    dirList = []  
    # 所有文件  
    fileList = []  
    # 返回一个列表，其中包含在目录条目的名称  
    files = os.listdir(path)  
    # 先添加目录级别  
    dirList.append(str(level))  
    for f in files:  
        if(os.path.isdir(path + '/' + f)):  
            # 排除隐藏文件夹。因为隐藏文件夹过多  
            if(f[0] == '.'):  
                pass  
            else:  
                # 添加非隐藏文件夹  
                dirList.append(f)  
        if(os.path.isfile(path + '/' + f)):  
            # 添加文件  
            fileList.append(path + '/' + f)  
    # 当一个标志使用，文件夹列表第一个级别不打印  
    i_dl = 0  
    for dl in dirList:  
        if(i_dl == 0):  
            i_dl = i_dl + 1  
        else:  
            # 打印至控制台，不是第一个的目录  
            #print '-' * (int(dirList[0])), dl  
            # 打印目录下的所有文件夹和文件，目录级别+1  
            _checkPath((int(dirList[0]) + 1), path + '/' + dl)  
    for fl in fileList:  
        # 打印文件  
        #print '-' * (int(dirList[0])), fl
        #print  fl[-3:]
        # 随便计算一下有多少个文件
        if fl[-3:].find(".py") >  -1:
            resultList.append(fl)
        allFileNum = allFileNum + 1

#读当前的文件并查看出日志
#规则先读出所有行，编辑后再重新写入
def _ReadFile(path):
    file = open(path,"r")
    lineList = []
    #是否需要修改标志
    needChange = False
    while True:
        line = file.readline()
        if not line:
            break
        lineList.append(line)
    for index in range(len(lineList)):
        line = lineList[index]
        test = TestCase()
        caseNum = -1
        if line.replace(' ','').find("#TestCase") > -1:
            test.strList.append("filename:" + path)
            count = 1
            while True:
                caseline = lineList[index + count]
                l = caseline.strip()
                print l.decode('utf-8').encode('gbk', 'ignore')
                if l[0] == "#":
                    test.strList.append(l[1:].strip())
                else:
                    test.strList.append(l.strip())
                    break
                count+=1
            s = line.strip(' ')
            s = s.replace('# ','#')
            l = s.split(' ')
            if len(l) > 1:
                test.CaseID = l[1].replace('\n','')
                print "upload testcase"
                res = _upload(test)
                if res["code"] > 0:
                    needChange = True
                else:
                    needChange = False
            else:
                print "insert testcase"
                res = _upload(test)
                id = res["result"]["id"]
                needChange = True
                line = line[:-1]+ " " + id + line[-1:]
                lineList[index] = line
                print lineList[index]
    file.close()
    #写回文件
    if needChange == True:
        file = open(path,"w")
        file.writelines(lineList)
        file.flush()
        file.close()
    return         

#上传测试用例
def _upload(case):
    upload = uploadTestCase()
    upload.id = case.CaseID
    upload.projectName = projectName
    for index in range(len(case.strList)):
        if case.strList[index].find("filename:") > -1:
            a = case.strList[index].replace("filename:","").strip(' ').split('\\')
            upload.fileName = a[len(a)-1]
        if case.strList[index].find("模块名称:") > -1:
            upload.moduleName = case.strList[index].replace("模块名称:","").strip(' ')
        if case.strList[index].find("方法:") > -1:
            upload.caseName = case.strList[index].replace("方法:","").strip(' ')
        if case.strList[index].find("描述:") > -1:
            upload.caseInfo = case.strList[index].replace("描述:","").strip(' ')
        if case.strList[index].find("依赖:") > -1:
            upload.preOrder = case.strList[index].replace("依赖:","").strip(' ')
        if case.strList[index].find("顺序号:") > -1:
            upload.caseOrder = case.strList[index].replace("顺序号:","").strip(' ')
        if case.strList[index].find("结果ID:") > -1:
            upload.resultID = case.strList[index].replace("结果ID:","").strip(' ')
        if case.strList[index].find("def ") > -1:
            upload.methodName = case.strList[index]
    return httpClass().UpLoadCase(upload)

def checkAllFile():
#检查当前项目中的所有py文件
    _checkPath(1, os.getcwd())  
    for f in resultList:
        if f.find(overFile) > -1:
            continue
        _ReadFile(f)

class TestCase():
    CaseID = ""
    strList = []
    def __init__(self):
        self.strList = []
        self.CaseID = ""

class uploadTestCase():
    id = ""
    projectName = ""
    moduleName = ""
    caseName = ""
    caseInfo = ""
    caseOrder = ""
    preOrder = ""
    methodName = ""
    className = ""
    fileName = ""
    resultID = ""


class httpClass():
    web = "192.168.145.20:8088"
    #web = "localhost:8080"
    baseurl = "/testsite/checktestcase";
    def __init__(self):
        pass
    def UpLoadCase(self,data):
        url = self.baseurl
        body = MyEncoder().encode(data)
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        conn = httplib.HTTPConnection(self.web)  
        conn.request("POST",url=url, body=body,headers=headers)

        response = conn.getresponse()
        data = response.read()
        a = MyDecoder().decode(data)
        #print a["id"]
        return a

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

