# coding:utf-8
'''
Created on 2016年02月15日

@author: shenlang
'''

from common.Cli import Cli
from urllib import unquote
from PIL._util import isStringType
from time import sleep
 
class SearchLib(Cli): 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def enterLeft(self):
        self.pressEnter()
        self.pressLeft()
    def enterEnter(self):
        self.pressEnter(2)
    def enterRight(self):
        self.pressEnter()
        self.pressRight()
    def enterUp(self):
        self.pressEnter()
        self.pressUp()
    def enterDown(self):
        self.pressEnter()
        self.pressDown()
        
    def inputSearchTxt(self,keyword):
        for k in keyword:
            self.pressUp(6)
            self.pressLeft(3)
            if k == '1':
                self.pressEnter()
            elif k == 'A':
                self.pressRight()
                self.enterLeft()
            elif k == 'B':
                self.pressRight()
                self.enterEnter()
            elif k == 'C':
                self.pressRight()
                self.enterRight()
            elif k == '2':
                self.pressRight()
                self.enterUp()
            elif k == 'D':
                self.pressRight(2)
                self.enterLeft()
            elif k == 'E':
                self.pressRight(2)
                self.enterEnter()
            elif k == 'F':
                self.pressRight(2)
                self.enterRight()
            elif k == '3':
                self.pressRight(2)
                self.enterUp()
            elif k == 'G':
                self.pressDown()
                self.enterLeft()
            elif k == 'H':
                self.pressDown()
                self.enterEnter()
            elif k == 'I':
                self.pressDown()
                self.enterRight()
            elif k == '4':
                self.pressDown()
                self.enterUp()
            elif k == 'J':
                self.pressDown()
                self.pressRight()
                self.enterLeft()
            elif k == 'K':
                self.pressDown()
                self.pressRight()
                self.enterEnter()
            elif k == 'L':
                self.pressDown()
                self.pressRight()
                self.enterRight()
            elif k == '5':
                self.pressDown()
                self.pressRight()
                self.enterUp()
            elif k == 'M':
                self.pressDown()
                self.pressRight(2)
                self.enterLeft()
            elif k == 'N':
                self.pressDown()
                self.pressRight(2)
                self.enterEnter()
            elif k == 'O':
                self.pressDown()
                self.pressRight(2)
                self.enterRight()
            elif k == '6':
                self.pressDown()
                self.pressRight(2)
                self.enterUp()
            elif k == 'P':
                self.pressDown(2)
                self.enterLeft()
            elif k == 'Q':
                self.pressDown(2)
                self.enterEnter()
            elif k == 'R':
                self.pressDown(2)
                self.enterRight()
            elif k == 'S':
                self.pressDown(2)
                self.enterDown()
            elif k == '7':
                self.pressDown(2)
                self.enterUp()
            elif k == 'T':
                self.pressDown(2)
                self.pressRight()
                self.enterLeft()
            elif k == 'U':
                self.pressDown(2)
                self.pressRight()
                self.enterEnter()
            elif k == 'V':
                self.pressDown(2)
                self.pressRight()
                self.enterRight()
            elif k == '8':
                self.pressDown(2)
                self.pressRight()
                self.enterUp()
            elif k == 'W':
                self.pressDown(2)
                self.pressRight(2)
                self.enterLeft()
            elif k == 'X':
                self.pressDown(2)
                self.pressRight(2)
                self.enterEnter()
            elif k == 'Y':
                self.pressDown(2)
                self.pressRight(2)
                self.enterRight()
            elif k == 'Z':
                self.pressDown(2)
                self.pressRight(2)
                self.enterDown()
            elif k == '9':
                self.pressDown(2)
                self.pressRight(2)
                self.enterUp()
    
    def inputHotWords(self):
        self.pressUp(2)
        hotwords = self.getSelectedViewText()
        self.pressEnter()
        hotword = hotwords.split(' ',1)
        print hotword
        return hotword[0]
    
    def SlectClass(self,class_name):
        self.pressRight(7)
        lastname = ''
        times = 0
        while True:
            times += 1
            self.pressDown()
            name = self.getSelectedViewText()
            if lastname == name:
                print 'all name read done, can not match'
                break
            lastname = name
            if class_name in name:
                break
        return times
    
    
    def choicResult(self):
        self.pressLeft()
        self.pressDown()
        self.pressRight()
        self.pressEnter()
        sleep(1)
        position = 6
        return position    
                
    def inputFullkeysetTxt(self,keyword):
        for k in keyword:
            self.pressUp(7)
            self.pressLeft(6)
            if k == 'A':
                self.pressEnter()
            elif k == 'B':
                self.pressRight()
                self.pressEnter()
            elif k == 'C':
                self.pressRight(2)
                self.pressEnter()
            elif k == '2':
                self.pressDown(4)
                self.pressRight(4)
                self.pressEnter()
            elif k == 'D':
                self.pressRight(3)
                self.pressEnter()
            elif k == 'E':
                self.pressRight(4)
                self.pressEnter()
            elif k == 'F':
                self.pressRight(5)
                self.pressEnter()
            elif k == '3':
                self.pressDown(4)
                self.pressRight(5)
                self.pressEnter()
            elif k == 'G':
                self.pressDown()
                self.pressEnter()
            elif k == 'H':
                self.pressDown()
                self.pressRight()
                self.pressEnter()
            elif k == 'I':
                self.pressDown()
                self.pressRight(2)
                self.pressEnter()
            elif k == '4':
                self.pressDown(5)
                self.pressEnter()
            elif k == 'J':
                self.pressDown()
                self.pressRight(3)
                self.pressEnter()
            elif k == 'K':
                self.pressDown()
                self.pressRight(4)
                self.pressEnter()
            elif k == 'L':
                self.pressDown()
                self.pressRight(5)
                self.pressEnter()
            elif k == '5':
                self.pressDown(5)
                self.pressRight()
                self.pressEnter()
            elif k == 'M':
                self.pressDown(2)
                self.pressEnter()
            elif k == 'N':
                self.pressDown(2)
                self.pressRight()
                self.pressEnter()
            elif k == 'O':
                self.pressDown(2)
                self.pressRight(2)
                self.pressEnter()
            elif k == '6':
                self.pressDown(5)
                self.pressRight(2)
                self.pressEnter()
            elif k == 'P':
                self.pressDown(2)
                self.pressRight(3)
                self.pressEnter()
            elif k == 'Q':
                self.pressDown(2)
                self.pressRight(4)
                self.pressEnter()
            elif k == 'R':
                self.pressDown(2)
                self.pressRight(5)
                self.pressEnter()
            elif k == 'S':
                self.pressDown(3)
                self.pressEnter()
            elif k == '7':
                self.pressDown(5)
                self.pressRight(3)
                self.pressEnter()
            elif k == 'T':
                self.pressDown(3)
                self.pressRight()
                self.pressEnter()
            elif k == 'U':
                self.pressDown(3)
                self.pressRight(2)
                self.pressEnter()
            elif k == 'V':
                self.pressDown(3)
                self.pressRight(3)
                self.pressEnter()
            elif k == '8':
                self.pressDown(5)
                self.pressRight(4)
                self.pressEnter()
            elif k == 'W':
                self.pressDown(3)
                self.pressRight(4)
                self.pressEnter()
            elif k == 'X':
                self.pressDown(3)
                self.pressRight(5)
                self.pressEnter()
            elif k == 'Y':
                self.pressDown(4)
                self.pressEnter()
            elif k == 'Z':
                self.pressDown(4)
                self.pressRight()
                self.pressEnter()
            elif k == '9':
                self.pressDown(5)
                self.pressRight(5)
                self.pressEnter()          
                
    def clearSearchTXT(self):  
        self.pressDown(3)
        self.pressLeft(3)
        self.pressEnter()
        
    def check_UTExposeLog(self,log,event=None,fromout=None,query=None,searchType=None,className=None,p=None,classp=None):
        log = eval(log)
        default_keys = ['yk_id','yk_name']
        data = log['businessInfo']['args']
        '''
        assert data['yk_id'] != '', 'error: yk_id is empty'
        assert data['yk_name'] != '', 'error: yk_id is empty'
        self.has_keys(data, default_keys)
        '''
        
        if type(data['query']) != type(1):
            print 'query is not a number'
            data['query'] = unquote(data['query'])
        
        if event == 'page_search_result':
            page_search_result_keys = ['from_out','query','search_id','search_type','result_cnt','class']
            self.has_keys(data, page_search_result_keys)
            
            if searchType == u'中文' and fromout not in ['com.yunos.tv.appstore','com.ali.tv.gamecenter','com.yunos.tv.edu']:
                assert data['scm_id'] != '', 'error: scm_id is empty'
            assert data['from_out'] == fromout, 'from_out error %s != %s' % (data['from_out'], fromout)
            assert data['query'] == query , 'query error %s != %s' % (data['query'], query)
            assert data['search_id'] != '', 'error: search_id is empty'
            assert unquote(data['search_type']) == searchType, 'search_type error %s != %s' % (data['search_type'], searchType)
            assert data['result_cnt'] > 0, 'result_cnt %s < 0' % data['result_cnt']
        
        elif event == 'click_search_result':
            click_search_result_keys = ['p','query','search_id','search_type','class','class_p','content_id',\
                                        'content_name','from_out']
            self.has_keys(data, click_search_result_keys)
            
            if searchType == u'中文':
                assert data['scm_id'] != '', 'error: scm_id is empty'
            assert data['p'] == p, 'position error %s != %s' % (data['p'],p)
            assert data['query'] == query , 'query error %s != %s' % (data['query'], query)
            assert data['search_id'] != '', 'error: search_id is empty'
            assert unquote(data['search_type']) == searchType, 'search_type error %s != %s' % (data['search_type'], searchType)
            assert data['class_p'] == classp, 'class position error %s != %s' % (data['class_p'],classp)
            assert data['content_id'] != '', 'error: content_id is empty'
            assert data['content_name'] != '', 'error: content_name is empty'
            assert data['from_out'] == fromout, 'from_out error %s != %s' % (data['from_out'], fromout)
            
        elif event == 'click_search_class':
            click_search_class_keys = ['query','search_id','class','result_cnt','search_type']
            self.has_keys(data, click_search_class_keys)
            assert data['query'] == query , 'query error %s != %s' % (data['query'], query)
            assert data['search_id'] != '', 'error: search_id is empty'
            print unquote(data['class'])
            assert unquote(data['class']) == className, 'class error %s != %s' % (data['class'], className)
            assert data['result_cnt'] > 0, 'result_cnt %s < 0' % data['result_cnt']
            assert unquote(data['search_type']) == searchType, 'search_type error %s != %s' % (data['search_type'], searchType)
        
        elif event == 'page_search_noresult':
            page_search_noresult_keys = ['query','search_type','search_id']
            self.has_keys(data, page_search_noresult_keys)
            assert data['query'] == query , 'query error %s != %s' % (data['query'], query)
            assert unquote(data['search_type']) == searchType, 'search_type error %s != %s' % (data['search_type'], searchType)
            assert data['search_id'] != '', 'error: search_id is empty'
            
        elif event == 'click_search_noresult':
            click_search_noresult_keys = ['p','query','search_type','search_id','class','content_id','content_name',\
                                          'from_out']
            self.has_keys(data, click_search_noresult_keys)
            assert data['p'] == p, 'p is not number'
            assert data['query'] == query , 'query error %s != %s' % (data['query'], query)
            assert data['search_id'] != '', 'error: search_id is empty'
            assert unquote(data['search_type']) == searchType, 'search_type error %s != %s' % (data['search_type'], searchType)
            assert data['content_id'] != '', 'error: content_id is empty'
            assert data['content_name'] != '', 'error: content_name is empty'
            assert data['from_out'] == fromout, 'from_out error %s != %s' % (data['from_out'], fromout)
            
    def has_keys(self,data,keys):
        '''
        功能：
        -检查给出内容中是否包含指定的所有key
        参数：
        -data:要校验key的数据，可以为dict或str
        -keys:期望data中包含的 keys
        返回值：
        -如果包含keys中所有的key，返回True；如果不是，返回False
        -类型：布尔
        例子：
        |has_keys|result|['id','name','price']|
        '''
        if type(data) in (str, unicode):
            data = eval(data)
        elif type(data) == dict:
            data = data
        extra = set(keys) - set(data.keys())
        if len(extra) == 0:
            return True
        else:
            print '%s do not has keys: %s' %(data.keys(), extra)
            return False
    
if __name__ == '__main__':
    ic = SearchLib('192.168.1.100')
#     ic.showScreensaver()
    ic.inputHotWords()
 
