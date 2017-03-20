# coding:utf-8
'''
Created on 2016.7.10

@author: shenlang
'''

#encoding=utf8
import hmac
import hashlib
import time
import json
import urllib
import urllib2
import subprocess
import inspect
import os
from Validator import validator


class MTop_4(object):
    '''
    
    功能描述 用于MTOP 4.0接口调用和检查
    
    依赖库：
    + requests
    '''
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    HOST = {'online': 'api.m.taobao.com',
            'prepare': 'acs.wapa.taobao.com',
            'daily': 'api.waptest.taobao.com'}
    
    def __init__(self, env='daily',api_name='',api_v=''):
        '''
        参数：
       - env 测试环境
        '''
        self.user_dict = {}
        self.host = MTop_4.HOST.get(env, MTop_4.HOST['daily'])
        print "self.host: %s" % self.host
        self.url = 'http://%s/gw' % self.host
        self.appKey = '4272' if env == 'daily' else '21800659'
        self.appSecret = '0ebbcccfee18d7ad1aebc5b135ffa906' if env == 'daily' else '68320bd5e9b06d4319bce709db1febfa'
        self.imei = '123456789012345'
        self.imsi = '123456789012345'
        self.ttid = '30000@taobao_android_5.1'#'123@taobao_android_5.1'#'123@tvmgr_yunos_1.0.0'
        self.pv='4.0'
        self.deviceId='123456'#'72e7566255dce0fa6ec6131fc18f8d61c47e59e9'
        self.split_str='&'

    def _generateSign4(self,baseStr,appSecret): 
        
        myhmac= hmac.new(appSecret,baseStr,hashlib.sha1)
        myhmac_hex= myhmac.hexdigest().encode('utf-8').rstrip('\n')
        #myhmac_hex2= base64.b64encode(myhmac.hexdigest())
        return myhmac_hex

    def _convertNull2Default( self,param):
        if param:
            return param
        else:
            return ''
    
    
    def  _convert2BaseStr(self, ecode, appkey, data, t,api,v,sid, ttid, deviceId, lat, lng):
        ecode = self._convertNull2Default(ecode)
        sid = self._convertNull2Default(sid)
        ttid = self._convertNull2Default(ttid)
        deviceId = self._convertNull2Default(deviceId)
        lat = self._convertNull2Default(lat) 
        lng = self._convertNull2Default(lng)

        original = [ecode, appkey, data, t,api,v,sid, ttid, deviceId, lat, lng]
        baseStr = self.split_str.join(original)
               
        print "baseStr: %s" % baseStr 
        return baseStr
    

    def _get_sign4(self,ecode, appkey, data, t, api, v, sid, ttid, deviceId, lat=None, lng=None):
        baseStr = self._convert2BaseStr(ecode, appkey, data, t, api, v, sid, ttid, deviceId, lat, lng);
        return self._generateSign4(baseStr, self.appSecret);

   
    def _request(self, url_params, headers,method='post'):
        #http://api.m.taobao.com/gw|h5|spcode|partner/{apiname}/{apiversion}/?data={params} &type=json|originaljson|jsonp&callback={callback function}&trace=tracetoken  
        url_api=url_params[0]
        url_para_json= url_params[1]
        print "mtop req url para:", url_para_json
        
        #print "mtop req headers:%s " % headers
        #print type(url_params[1]),url_params[1]

        if url_para_json.has_key('data'):
            for k, v in url_para_json.iteritems(): 
                if k == 'data':
                    url = '%s?%s' % (url_api,'&'.join(['%s=%s' % (k, urllib.quote(json.dumps(v,separators=(',',':')))) ]))
                else:
                    url ='%s&%s' % (url, '&'.join(['%s=%s' %(k, urllib.quote(v))]))
                
                #print " v---%s" % v
        else:
            url = '%s?data={}' % url_api
           
        #url = '%s?%s' % (url_params[0], '&'.join(['%s=%s' % (k, urllib.quote(v)) for k, v in url_params[1].iteritems()]))
        print "mtop req url:%s " % url        
               
        request = urllib2.Request(url, None,headers)  

        try:  
            response = urllib2.urlopen(request)
        except urllib2.HTTPError,e:
            print e.reason
        data = response.read()

        print "------http response: -------"
        if data:
            json_format_str = json.dumps(data, indent=4, ensure_ascii=False)
            print json_format_str

        return data

    def _param_url(self, api,  v, url_data, callback=None, trace=None):
        url = '%s/%s/%s/' % (self.url,api,v)
        url_dataJson={}
        url_dataJson['data']=url_data
        #data = json.dumps(url_data)
        
        print json.dumps(url_dataJson)
        return [url,url_dataJson]

    def _param_header(self,  api,  v,data, deviceId=None, ecode=None, sid=None):
        t = str(int(time.time()))
        if data == None:
            data = ''
        data = json.dumps(data,separators=(',',':'))
        sign = self._get_sign4(ecode,self.appKey,data,t,api,v,None,self.ttid, deviceId,None,None)
        #print "sign: %s" % sign
        return {
                'm-pv':self.pv,
                'm-ttid': self.ttid,
                'm-t': t,
                'm-devid': self.deviceId,
                'm-appKey': self.appKey,
                'm-sign': sign,
                }
    
    def mtop(self, api, v='1.0', deviceId='', user=None, passwd=None, simple=False, printUrl=True, printResult=True, **kwargs):
        '''
        功能：
        - 按照MTOP API4.0协议封装的接口，默认使用POST请求和simple签名方式，若指定用户名密码则自动使用ecode签名。
        '''
        param_data, param_validator = {}, {}
        for key, value in kwargs.iteritems():
            #print "key=%s: value=%s" % (key,value)            
            if key.startswith('_'):
                param_validator[key] = value
            else:
                param_data[key] = value

        ecode, sid = '', ''
        if user and passwd:
            _user = self._login(user, passwd)
            if not simple:
                ecode = _user['ecode']
            sid = _user['sid']
        #print "param_data: %s" % param_data
        jsond = json.loads(self._request(self._param_url(api, v,param_data), self._param_header(api, v, param_data, self.deviceId, ecode, sid)))
        #jsond = json.loads(self._request(self._param_url(api, v,param_data), self._param_header(api, v, param_data, None, None, None)))
        with_error = param_validator.pop('__with_error') if '__with_error' in param_validator else 'SUCCESS'
        print "with_error: %s" % with_error
        if with_error.lower() != 'ignore':
            assert with_error in jsond['ret'][0], u'%s not in %s' % (with_error, jsond['ret'][0])
        result = jsond.get('data')
        validator.validate(result, **param_validator)
        return result

    def _md5hex(self, data):
        return hashlib.md5(data).hexdigest()

    def _getAppToken(self, user):
        data = self.mtop('com.taobao.client.sys.getAppToken', 'v2', key=user)
        n, e = data['pubKey'].splitlines()
        return data['token'], int(n), int(e)
    
    def _encrypt(self, n, e, target):
        this_file = inspect.getfile(inspect.currentframe())
        this_dir = os.path.abspath(os.path.dirname(this_file))
        cmd = 'java -jar %s/rsa.jar %s %s %s' % (this_dir, n, e, target)
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    
    def _login(self, username, password='taobao1234'):
        if not self.user_dict.has_key(username):
            token, n, e = self._getAppToken(username)
            password = self._encrypt(n, e, password)
            user = self.mtop('com.taobao.client.sys.login', 'v2', token=token, username=username, password=password)
            print user
            self.user_dict[username] = user
        return self.user_dict[username]
    
if __name__ == '__main__':
    pass