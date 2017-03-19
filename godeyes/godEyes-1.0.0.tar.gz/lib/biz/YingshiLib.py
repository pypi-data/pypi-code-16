# coding:utf-8
'''
Created on 2016年11月12日

@author: shenlang
'''

import re
import json
from common.Cli import Cli
from common.Http import Http
from common.MTop_4 import MTop_4
import xml.etree.ElementTree as ET
from common.Validator import validator
from common import Util
 
class YingshiLib(Cli): 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    
    
    def closeUpgradeDialog(self,ip=None):
        text = self.getPageText(ip)
        if '已为您更新至最新内测版' in text:
            self.inputKeyEvent(4,ip)
            text = self.getPageText(ip)
            assert '已为您更新至最新内测版' not in  text,"closeDialog fail:after closeDialog current window text is %s" %  text     
    
    def firstGotoYingshiDetail(self,ip=None):
        self.closeUpgradeDialog(ip)
        topActivity = self.getTopActivity(ip)
        print topActivity;
        if topActivity == 'com.yunos.tv.yingshi.activity.GuiderAcitivty' or topActivity == 'com.yunos.tv.yingshi.boutique.bundle.guider.GuiderActivity':
            
            self.inputKeyEvent(22, ip)
            self.inputKeyEvent(22, ip)
            self.inputKeyEvent(22, ip)
            self.inputKeyEvent(22, ip)
            self.waitForTopActivity('com.yunos.tv.yingshi.activity.YingshiHomeActivityV5',ip)
            temp_txt = self.getPageText(ip)
            if temp_txt == "":
                self.inputKeyEvent(4, ip)
    
    def recommend(self,appid,ip=None,**kwargs):
        uuid = self.getUUID(ip)
        http = Http()
        url = 'https://tui.taobao.com/recommend?appid=%d&utdid=%s&debug=true' % (appid,uuid)
        if appid == 2865:
            key = 'program_id'
            url = url + '&' + key + '=' + str(kwargs[key])
        return http.get(url, json)
    
    
    def assembleSystemInfo(self,ip=None,packageName='com.yunos.tv.yingshi.boutique'):
        mediaAbility = self.getMediaAbility(ip)
        systemVersion = self.getSystemVersion(ip)
        uuid = self.getUUID(ip)
        deviceModel = self.getDeviceModel(ip)
        versionCode = self.getAppVersionCode(packageName, ip)
        systemInfoDict = {'mac':'','sw':'','from':'0,7,9','charge_type':'2,3,5'}
        systemInfoDict['device_media'] = mediaAbility
        systemInfoDict['device_model'] = deviceModel
        systemInfoDict['device_system_version'] = systemVersion
        systemInfoDict['uuid'] = uuid
        systemInfoDict['version_code'] = versionCode
        return json.dumps(systemInfoDict)
    
    
    
    
    
    def goToCatalogListView(self,catalogName,ip=None,packageName='com.yunos.tv.yingshi.boutique'):
        
        
        catalogName = Util.urlEncode(catalogName)
        
        def getExtraStrByCatalogName(argument):
            switcher = {
                '%E7%94%B5%E5%BD%B1' : '1',
                '%E7%94%B5%E8%A7%86%E5%89%A7' : '2',
                '%E7%BB%BC%E8%89%BA' : '200' ,
                '%E5%8A%A8%E6%BC%AB' : '180' ,
                '%E7%BA%AA%E5%AE%9E' : '171' ,
                '%E6%96%B0%E9%97%BB' : '133' ,
                '%E4%BD%93%E8%82%B2' : '143' ,
                '%E7%94%9F%E6%B4%BB' : '182' ,
                '%E6%90%9E%E7%AC%91' : '220' ,
                '%E9%9F%B3%E4%B9%90' : '552' ,
            }
            return switcher.get(argument, 'error')
        
        def getfilterChannelByCatalogName(argument):
            switcher = {
                '%E7%94%B5%E5%BD%B1' : 'M',
                '%E7%94%B5%E8%A7%86%E5%89%A7' : 'T',
                '%E7%BB%BC%E8%89%BA' : 'A',
            }
            return switcher.get(argument, 'error')
        
        m = MTop_4('online')
        api_v='1.0'
        api_name='mtop.tvdesktop.v5video.getintent'
        systemInfo = self.assembleSystemInfo(ip,packageName)
#         systemInfo = '{"uuid":"B283D77B40BC76A585C8FD7FC4114D7A","device_model":"MagicBox_M13","device_system_version":"3.0.4","device_sn":"B283D77B40BC76A5","device_firmware_version":"3.0.4-RS-20160731.0049","firmware":"3.0.4-RS-20160731.0049","charge_type":"2,3,5","sw":"sw1080","version_code":2100501105,"yingshi_version":2100501105,"device_media":"dolby,h265_4k2k,drm","mac":"D84710D1D0C8","ethmac":"D84710D1D0C8","from":"0,7,9","license":"1","bcp":"1","v_model":"F"}'
        
        print 'systemInfo:%s' % systemInfo
        extraStr = getExtraStrByCatalogName(catalogName)
        print 'extraStr:%s' % extraStr
        
        ret = m.mtop(api_name,api_v, action='CATALOG',extra=extraStr, system_info=systemInfo)
        initNodeList = ret['extra']['nodeList']
        nodelist = json.dumps(initNodeList)
        print nodelist
        
        filterChannel = getfilterChannelByCatalogName(catalogName)
        print 'filterChannel:%s' % filterChannel
        
        print 'catalog=%s' % nodelist
        
        
        if extraStr in ['200','180']:
            cmd = 'yunostv_yingshi://yingshi_catalog?catalog_name=%s&catalog=%s' % (catalogName,nodelist)
        else:
            nodeId = extraStr
            cmd = 'yunostv_yingshi://yingshi_catalog?catalog_name=%s&filterChannel=%s&nodeId=%s&catalog=%s' % (catalogName,filterChannel,nodeId,nodelist)
        newCmd = re.sub(r'"', r'\"', cmd)
        self.startActivityWithURI(newCmd, ip)
    
    
    def jumpToMovieListView(self,ip=None):
        self.goToCatalogListView('电影',ip)
    
    
    def jumpToDramasListView(self,ip=None):
        self.goToCatalogListView('电视剧',ip)
    
    def jumpToVarietyListView(self,ip=None):
        self.goToCatalogListView('综艺',ip)
    
    def getSelectedGroupTitle(self, ip=None, **kwargs):    
        xml_sz = self.getHxml(ip)
        if xml_sz == '':
            self.logInfo('dump失败')
            return None
        else:
            tree = ET.fromstring(xml_sz)
            title = ''
            parent_elem = None
            title_elem = None
            index = -1
            parent_map = dict((c, p) for p in tree.getiterator() for c in p)
            for elem in tree.iter(tag='node'):
                if elem.attrib['selected'] == 'true' and elem.attrib['focused'] == 'true':
                    parent_elem = parent_map[elem]
                    index= int(elem.attrib['index'])
                    break
            for i in range(index):
                if parent_elem[index - i - 1].attrib['resource-id'] == "com.yunos.tv.yingshi.boutique:id/title":
                    title_elem=parent_elem[index - i - 1]
                    title = title_elem.attrib["text"]
                    for elem in title_elem:
                        title = title + " " + elem.attrib["text"]
                    break
            title = title.strip()
            validator.validate(title, **kwargs)
            return title
        
    def getAppVersionName(self,packageName,ip=None):  
        if packageName is None:
            return ''
        rets = self.adb_shell('dumpsys package %s | grep versionName' % packageName,ip=ip,pattern=r'versionName=(.*)') 
        print rets
        
        if type(rets) == list:
            for ret in rets:
                if 'MagicBox_Yingshi' not in ret:
                    ret = 'MagicBox_Yingshi_R_' + ret.strip() + '_1d433747'
                return ret.strip()
                 
        else:
            if 'MagicBox_Yingshi' not in rets:
                    rets = 'MagicBox_Yingshi_R_' + rets.strip() + '_1d433747'
            return rets.strip()        
   

if __name__ == '__main__':
    l = YingshiLib('30.11.32.135')
    print l.jumpToVarietyListView()
    # print l.getAppVersionName('com.yunos.tv.yingshi.boutique', '192.168.1.110')
