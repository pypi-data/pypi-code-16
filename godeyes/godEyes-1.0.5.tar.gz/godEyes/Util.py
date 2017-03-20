# coding:utf-8
import json
import os
import re
import time
from urllib import unquote
from urllib import quote
import yaml

from globalVal import rootdir, TAG




def get_root_dir():
    return rootdir


def checkpoint_fail(msg, exp, act, debug_info=None):
    if debug_info is not None:
        print debug_info
    err_msg = u'【错误描述】 : %s;【期望结果】 : %s;【实际结果】 : %s' % (msg, exp, act)
    raise Exception(err_msg)


def check_ret(exp, act):
    if exp != act:
        checkpoint_fail(u'检查返回值失败', exp, act)

def timestampMillis():
        return long(time.time() * 1000)     

def getCurDir():
    return os.path.abspath(os.curdir)

def getCTime():
    timeArray = time.localtime(time.time())
    return time.strftime("%Y%m%d%H%M%S", timeArray)

def urlDecode(string):
    return unquote(string).decode('UTF-8')

def urlEncode(string):
    return quote(string)

def formatLogcatTime(logcatTime):
    logcatTimes = logcatTime.split('.')
    year = time.strftime('%Y',time.localtime(time.time()))
    t = year + '-' + logcatTimes[0]
    
    time1 = long(time.mktime(time.strptime(t,'%Y-%m-%d %H:%M:%S')) *1000) 
    time2 = long(logcatTimes[1])
    return time1 + time2


     
def getUTVersion(filePath,keyword='',customFilter='',pid=''):
    with open(filePath) as f:
        for line in f:
            if 'Analytics.' in line and keyword in line and customFilter in line and pid in line:
                return 6
            elif 'UTMini' in line and 'cache_log:::' in line  and keyword in line and customFilter in line and pid in line:
                return 5
            elif 'I/cache_log' in line and 'UT:' in line and keyword in line and customFilter in line and pid in line:
                return 4                 
        
        return 0    
        

def readFile(filePath,pageName,eventId,arg1,beginTime=0L,endTime=0L,customFilter='',pid=''):
        
        utLogList = []
        if pageName and eventId: 
            keyword = '%s||%s||%s' % (pageName,eventId,arg1) 
            print '%sfilter keyword:%s' % (TAG,keyword)
            utVersion = getUTVersion(filePath,keyword,customFilter,pid)
            with open(filePath) as f:
                if utVersion == 6:
                    for line in f:
                        if 'Analytics.' in line and 'Log:' in line and keyword in line and customFilter in line and pid in line:
                            fLogcatTime = _getFLogcatTime(line)
                            if beginTime:
                                if beginTime > fLogcatTime:
                                    continue
                            if endTime: 
                                if endTime < fLogcatTime:
                                    continue     
                            utLogList.append(line)
                        
                elif utVersion == 5:
                    for line in f:   #update 只过滤cacheLog
                        if 'UTMini' in line and 'cache_log:::' in line and keyword in line and customFilter in line and pid in line:
                            fLogcatTime = _getFLogcatTime(line)
                            if beginTime:
                                if beginTime > fLogcatTime:
                                    continue
                            if endTime: 
                                if endTime < fLogcatTime:
                                    continue     
                            utLogList.append(line)
                            
                     
                elif utVersion == 4:
                    for line in f:
                        if 'I/cache_log' in line and 'UT:' in line and keyword in line  and customFilter in line and pid in line:
                            fLogcatTime = _getFLogcatTime(line)
                            if beginTime:
                                if beginTime > fLogcatTime:
                                    continue
                            if endTime: 
                                if endTime < fLogcatTime:
                                    continue     
                            utLogList.append(line)
        return utLogList,utVersion       

def _getFLogcatTime(line):
    times = line.split()
    logcatTime = times[0] + ' ' + times[1]
    fLogcatTime = formatLogcatTime(logcatTime)
    print 'fLogcatTime:%ld' % fLogcatTime
    return fLogcatTime                  

def sequenceCheckUtLog(utLogList,eventId=0,arg1='',needSequenceCheck=True):
    # 检查相关log总条数
    print TAG + 'print utLogList'
    for l in utLogList:
        print l
    logListLength = len(utLogList)
    
    strFromPostLogList = []
    
    if not needSequenceCheck:
        strFromPostLogList = utLogList
    else:
        if arg1 and arg1.startswith('exposure') or arg1.startswith('Exposure_') or 'expose' in arg1:
            assert logListLength >= 1 ,'logListLength < 1,actual length is %d' % logListLength
            
            #assert logListLength >= 3 ,'logListLength < 3,actual length is %d' % logListLength
            
            for utLog in utLogList:
                if 'Analytics.' in utLog and 'Log:' in utLog:
                    strFromCacheLog = utLog.lstrip('Log:')
                    strFromCacheLog = strFromCacheLog.strip()
                    print '%sstrFromCacheLog:%s' % (TAG,strFromCacheLog)
                    strFromPostLogList.append(strFromCacheLog)
                    
                elif 'cache_log:::' in utLog:
                    cacheLog = utLog[(utLog.find('cache_log:::')):] 
                    print '%scacheLog:%s' % (TAG,cacheLog)
                    assert cacheLog.startswith('cache_log:::') and 'I/UTMini' in utLog,'(cache log) format error:%s' % utLog
                    strFromCacheLog = cacheLog.lstrip('cache_log:::')
                    strFromCacheLog = strFromCacheLog.strip()
                    print '%sstrFromCacheLog:%s' % (TAG,strFromCacheLog)
                    strFromPostLogList.append(strFromCacheLog)
#                 if 'UTSqliteLogStore:::insert log' in utLog:
#                     assert 'D/UTMini' in utLog,'(sqlite log) format error:%s' % utLog
#                     if eventId:
#                         assert 'eventId=%s' % eventId in utLog,'third log(sqlite log) format error:%s' % utLog
#                     assert 'isSuccess:true' in utLog,'insert sqlite fail'
#                 
#                 if 'content:::' in utLog and 'post' in utLog:
#                     postLog = utLog[(utLog.find('content:::')):]
#                     #     print 'postLog:%s' % postLog
#                     assert 'I/UTMini' in utLog and postLog.startswith('content:::'),'fouth log(post log) format error:%s' % utLog
#                     strFromPostLog = postLog.lstrip('content:::')           
#                     strFromPostLogList.append(strFromPostLog)
    
        else:
            #assert logListLength == 3 ,'logListLength !=3,actual length is %d' % logListLength
            assert logListLength == 1 ,'logListLength !=1,actual length is %d' % logListLength
            # 第一条log
            utLog = utLogList[0]
            if 'Analytics.' in utLog and 'Log:' in utLog:
                strFromCacheLog = utLog.lstrip('Log:')
                strFromCacheLog = strFromCacheLog.strip()
                print '%sstrFromCacheLog:%s' % (TAG,strFromCacheLog)
                strFromPostLogList.append(strFromCacheLog)
            
            elif 'cache_log:::' in utLog: 
            
                cacheLog = utLog[(utLog.find('cache_log:::')):] 
                print '%scacheLog:%s' % (TAG,cacheLog)
                
                assert cacheLog.startswith('cache_log:::') and 'I/UTMini' in utLogList[0],'second log(cache log) format error:%s' % utLogList[0]
                strFromCacheLog = cacheLog.lstrip('cache_log:::')
                strFromCacheLog = strFromCacheLog.strip()
                print '%sstrFromCacheLog:%s' % (TAG,strFromCacheLog)
                strFromPostLogList.append(strFromCacheLog)
            
            '''
            # 第二条log
            assert 'D/UTMini' in utLogList[1] and 'UTSqliteLogStore:::insert log' in utLogList[1],'third log(sqlite log) format error:%s' % utLogList[1]    
            if eventId:
                assert 'eventId=%s' % eventId in utLogList[1],'third log(sqlite log) format error:%s' % utLogList[1]
            assert 'isSuccess:true' in utLogList[1],'insert sqlite fail'
            
            untreatedSqlLog = utLogList[1][(utLogList[1].find('content=')):].lstrip('content=')
            i= untreatedSqlLog.find(', time=')
            strSqlLog = untreatedSqlLog[:i]
            strSqlLog = strSqlLog.strip()   
            print '%strFromCacheLog:%s' % (TAG,strFromCacheLog)
            print '%sstrSqlLog:%s' % (TAG,strSqlLog)
            assert  strFromCacheLog == strSqlLog,'strFromCacheLog != strSqlLog'
            
            # 第三条log
            postLog = utLogList[2][(utLogList[2].find('content:::')):]
            #     print 'postLog:%s' % postLog
            assert 'I/UTMini' in utLogList[2] and 'post' in utLogList[2] and postLog.startswith('content:::'),'fouth log(post log) format error:%s' % utLogList[2]
            strFromPostLog = postLog.lstrip('content:::')
            strFromPostLog = strFromPostLog.strip()
            
            assert  strFromCacheLog == strFromPostLog,'strFromCacheLog != strFromPostLog' 
			
            strFromPostLogList.append(strFromPostLog)
			'''
            
    
    
    return strFromPostLogList
    
def _getContent(string):
    p = re.compile('\[(.*)\]')
    result = p.findall(string)
    if len(result) == 1:
        result = result[0]
    
    rets = result.split(',')
    print rets
    for ret in rets:
        if 'content=' in ret:
            print ret
            return ret[(ret.find('content=')+len('content=')):]  


def splitByComma(argString):
    
    
    p = re.compile(u'([a-zA-Z0-9_]+=[\u4e00-\u9fa5aa-zA-Z0-9_,.~·()，&?\[\]{}:;\-+%"\s]+),')
    argStrs1 = p.findall(argString)
    
    p2 = re.compile(u',([a-zA-Z0-9_]+=[\u4e00-\u9fa5aa-zA-Z0-9_.~·()，&?\[\]{}:;\-+%"\s]+)')
    result = p2.findall(argString)
    
    if len(result) > 0:
        argStrs1.append(result[-1])
#     print 'after append argStrs1:%s' % argStrs1
    p3 = re.compile(r'([a-zA-Z_]+=)')
    argStrs2 = p3.findall(argString)
#     print 'argStrs2:%s' % argStrs2
    
    def exist(string, argStrs):
        for arg in argStrs:
            if string in arg:
                return True
    
    for argstr in argStrs2:
        if not exist(argstr, argStrs1):
            argStrs1.append(argstr)
            
    argStrs3 = list(set(argStrs1))
    argStrs3.sort(key=argStrs1.index)
    return argStrs3

def splitByEqual(argString):
    return argString.split(',')


def _formatByStrategy(strategyName, string):
    switcher = {
        'valueNoEqual' : splitByComma,
        'valueNoComma' : splitByEqual,
    }
            
    return switcher.get(strategyName)(string)
        
def formatUTLog(logStr):
    
    
 
    strs = logStr.split('||',28)
    sessionDic = {}
    sessionDic['brand'] = strs[2]
    sessionDic['deviceModel'] = strs[3]
    sessionDic['resolution'] = strs[4]
    sessionDic['access'] = strs[6]
    sessionDic['appKey'] = str(strs[9])
    sessionDic['appVersionName'] = strs[10]
    sessionDic['osVersion'] = strs[17]
    sessionDic['sdkVersion'] = strs[18]
    
    extraDic = {}
    extraInfo = strs[26]
    if '=' in extraInfo:
        extraStrs = extraInfo.split(',') 
        for tempExtraStr in extraStrs:
            extraEntry =tempExtraStr.split('=')
            extraDic[extraEntry[0]] = extraEntry[1]
    
    sessionDic['extra'] = extraDic  
    sessionDic['timestamp'] = strs[27]
    
    businessInfo = strs[-1]
#     print businessInfo
    businessStrs = businessInfo.split('||')
    businessDic = {}
    businessDic['pageName'] = businessStrs[0]
    businessDic['eventId'] = int(businessStrs[1])
    businessDic['arg1'] = businessStrs[2]
    businessDic['arg2'] = businessStrs[3]
    businessDic['arg3'] = businessStrs[4]
    
    argStr = businessStrs[5]
    argDic = {}

    argStr = argStr.decode('utf-8')
    equalCount = argStr.count('=')
    print 'equalCount:%d' % equalCount
    commaCount = argStr.count(',')
    print 'commaCount:%d' % commaCount
    
    if equalCount >= (commaCount+1):
        argStrs = _formatByStrategy('valueNoComma', argStr)
    else:
        repaireDict = {}
        argStrs = _formatByStrategy('valueNoComma', argStr)
        for arg in argStrs:
            if arg.count('=') > 1:
                tempArgs = arg.split('=', 1)
                repaireDict[tempArgs[0]] = tempArgs[1]
        argStrs = _formatByStrategy('valueNoEqual', argStr)
        
        
        def replaceNewValue(d,string):
            for key in d:
                if string.startswith(key):
                    return key + '=' + str(d[key])
                
                
        def isRedundancy(d,string):
            for key in d.values():
                if string in key:
                    return True           
        
        for i, arg in enumerate(argStrs):
            newValue = replaceNewValue(repaireDict,arg)
            if newValue:
                argStrs[i] = newValue
            if isRedundancy(repaireDict,arg):
                argStrs.remove(arg) 
        
    for arg in argStrs:
        
        arg = arg.strip()
        if '=' in arg:
            tempArgs = arg.split('=', 1)
            if tempArgs[1].isdigit():
                argDic[tempArgs[0]] = int(tempArgs[1])
            else:        
                argDic[tempArgs[0]] = tempArgs[1] 
        else:
            i = argStrs.index(arg)
            i = i - 1
             
            if '=' in argStrs[i]:
                tArgs = argStrs[i].split('=')
                argDic[tArgs[0]] = tArgs[1] + ',' + str(arg)
                
    businessDic['args'] = argDic
    
    infoDic = {}
    infoDic['sessionInfo'] = sessionDic
    infoDic['businessInfo'] = businessDic
    
    return json.dumps(infoDic)

def argsStrToJson(string):
    string = string.decode('utf-8')
    count = string.count('=')
    if count >1:
        p = re.compile(u'(.*),')
        argStrs = p.findall(string)
        print argStrs
    
        p = re.compile(u',([^,]+)')
        result = p.findall(string)
        argStrs.append(result[-1])
        print argStrs
    elif count == 1:
        argStrs.append(string)
     
    argDic = {}
     
    for arg in argStrs:
         
        arg = arg.strip()
        if '=' in arg:
            tempArgs = arg.split('=')
            if tempArgs[1].isdigit():
                argDic[tempArgs[0]] = int(tempArgs[1])
            else:        
                argDic[tempArgs[0]] = tempArgs[1] 
             
         
    return json.dumps(argDic) 

def is_json(myjson):  
    try:  
        json.loads(myjson)  
    except ValueError:  
        return False  
    return True 

def jsonToPythonType(jsonStr):  
    return json.loads(jsonStr)  

def loadYamlFromFile(filePath):
    with open(filePath, 'r') as f:
        return yaml.load(f)

def getAppKey(appInfoConfigPath, packageName):
    #os.path.join(rootdir, 'godEyes', 'appInfo.yml')
    dList = loadYamlFromFile(appInfoConfigPath)
    appKey = ''
    appKeyList = []
    for d in dList:
        if d['packageName'] == packageName:
            tempAppKey = d['appKey']
            if type(tempAppKey) != str:
                tempAppKey = str(tempAppKey)
            appKeyList.append(tempAppKey)
    if len(appKeyList) == 1:
        appKey = appKeyList[0]
    return appKey


def getAppName(packageName):
    dList = loadYamlFromFile(os.path.join(rootdir, 'uttest', 'ci', 'appInfo.yml'))
    appName = ''
    for d in dList:
        if d['packageName'] == packageName:
            appName = d['appName']
            return appName


def getFormatLogList(logcatPath,pageName,eventId,arg1='',beginTime=0L,endTime=0L,needSequenceCheck=True,customFilter='',pid=''):
        
        utLogList,utVersion = readFile(logcatPath,pageName,eventId,arg1,beginTime,endTime,customFilter,pid)
        print TAG + 'utVersion:' + str(utVersion)
        if utVersion < 5:
            needSequenceCheck = False
            
        initialPostLogList = sequenceCheckUtLog(utLogList,eventId,arg1, needSequenceCheck)
        print '%sinitialPostLogList:%s' % (TAG,initialPostLogList)
        
        formatLogList = []
        for initialPostLog in initialPostLogList:
            formatLog = formatUTLog(initialPostLog)
            print '%sformatLog:%s' % (TAG,formatLog)
            formatLogList.append(formatLog)
        
        return formatLogList   


def hasNotPost(logcatPath,pageName,eventId,arg1='',beginTime=0L,endTime=0L,customFilter=''):
        formatLogList = getFormatLogList(logcatPath,pageName,eventId,arg1,beginTime,endTime,False,customFilter)
        l = len(formatLogList)
        assert l == 0,'actual has post count:%d' % l


def cherryBestLocatorTuple(ymlPath, pageName,elementName):
        locator = None 
        r = loadYamlFromFile(ymlPath) 
        
        print r
        
        elementsList = []
        
        sameNameList = []
        
        for d in r:
            pageDict = d['page']
            if pageDict['pageName'] == pageName:
                
                elementsList = pageDict['elements']
                
                for element in elementsList:
                    if element['name'] == elementName:
                        sameNameList.append(element)
                
                if len(sameNameList) == 0:
#                     raise LocatorNotFoundError('pageName:%s' % pageName + ' and elementName:%s' % elementName + ' is not found in %s' % ymlPath) 
                    return locator
                maxPriority = sameNameList[0]['priority']
                maxIndex = 0
                for i, ele in enumerate(sameNameList):
                    tempPri = ele['priority']
                    if tempPri > maxPriority:
                        maxPriority = tempPri
                        maxIndex = i
                by = sameNameList[maxIndex]['findBy']        
                locator = sameNameList[maxIndex]['value']
                
        return by,locator

def cherryBestLocator(self, ymlPath, pageName,elementName):
        locator = None 
        r = loadYamlFromFile(ymlPath) 
        
        print r
        
        elementsList = []
        
        sameNameList = []
        
        for d in r:
            pageDict = d['page']
            if pageDict['pageName'] == pageName:
                
                elementsList = pageDict['elements']
                
                for element in elementsList:
                    if element['name'] == elementName:
                        sameNameList.append(element)
                
                if len(sameNameList) == 0:
#                     raise LocatorNotFoundError('pageName:%s' % pageName + ' and elementName:%s' % elementName + ' is not found in %s' % ymlPath) 
                    return locator
                maxPriority = sameNameList[0]['priority']
                maxIndex = 0
                for i, ele in enumerate(sameNameList):
                    tempPri = ele['priority']
                    if tempPri > maxPriority:
                        maxPriority = tempPri
                        maxIndex = i
                        
                locator = sameNameList[maxIndex]['value']
                
        return locator

def setCommonParamDict(**kwargs):
        return kwargs

if __name__ == '__main__':
    s = getAppKey(os.path.join(rootdir, 'uttest', 'ci', 'appInfo.yml'), 'com.yunos.tv.yingshi.boutique')
    print s

#     1489023402475
#     1489023387000
#     a = getAppKey('com.yunos.tv.universalsearch')
#     print a
#     print a == '23330016'
#     with open(rootdir + '/config/appInfo.yml', 'r') as f:
#         s = yaml.load(f)
#         packageName = 'aa'
#         for i in s:
#             if i['packageName'] == packageName:
#                 print i['appKey']
#     utLogList,version = readFile('/Users/panluhai/Documents/workspace/uttest/logs/logcat20170221094937_30.11.70.24.log','UT',19999,'sys_error_event',pid='2045')
#     utLogList,version = readFile('/Users/panluhai/Documents/workspace/uttest/logs/logcat20161214142336_192.168.1.30.log','UT',19999,'YingshiDetail_enter')
#     print version
#     print utLogList
#     sequenceCheckUtLog(utLogList,19999,'exposure_yingshi')
#     print urlEncode('综艺')
#     a = 'isTrial=false,isVip=false,isBelongTBO=false,isBelongMovies=true,from=Homeshell,from_self=YingshiDetail,from_scm=null,scm_id=[{"scm":"1007.12865.67098.0","ids":"[142675, 134734, 133545, 152035, 143625, 153206, 144542, 23612, 114146, 151929, 110933, 152985]"}],hasPromoTicket=false,showType=3,video_id=160300,is_login=false,channel_name=电视剧,video_type=false,from_act=null,isPurchased=true,source=7,video_name=放弃我,抓紧我(TV版),member_name=null'
#     a = 'scm_id=[{"scm":"1007.12865.67098.0","ids":"[142675, 134734, 133545, 152035, 143625, 153206, 144542, 23612, 114146, 151929, 110933, 152985]"}],source=7'
#     a =  'video_name=放弃我,抓紧我(TV版),member_name=null'
#     a = 'source=7,video_name=放弃我,抓紧我(TV版),member_name=null'
#     print formatUTLog(a)
#     print argsStrToJson(a)
#     print len(result)
#     print type(result)
#     print result[-1]
#     print result
# #     d = jsonToPythonType(c)
# #     e = d['video_name']
# #     print e == b
#     b = 'scm_id=%5B%7B%22scm%22%3A%221007.13294.33285.0%22%2C%22ids%22%3A%22%5B158447%2C+160345%2C+158477%2C+158632%2C+133406%2C+160162%2C+160027%2C+155860%2C+155862%2C+118674%2C+159558%2C+22128%2C+158488%2C+134418%2C+158448%2C+156595%2C+158449%2C+157983%2C+159044%2C+160011%5D%22%7D%5D,class=%E7%94%B5%E5%BD%B1'
#     print argsStrToJson(b)
