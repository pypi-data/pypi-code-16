#encoding=utf8
'''
Created on 2017.1.14

'''
import copy
import json
import os
import re
import tempfile
from urllib import urlretrieve

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn,RobotNotRunningError

b = BuiltIn()

try:
    from PIL import Image
except:
    logger.warn('can import Image, pip install Pillow', True)

FLAG = '__'


class Validator(object):
    '''

    
    '''
    def __init__(self):
        
        pass
    
    def __get_result_and_operate(self, result, key):
        r = copy.deepcopy(result)
        key = key.replace('___', '*')
        keys = key.split(FLAG)
        if len(keys) == 2:
            ks, op = keys[0], keys[1] if keys[1] else 'equal'
        elif len(keys) == 1:
            ks, op = keys[0], 'equal'
        else:
            raise Exception('unknown validator')
#         logger.debug('ks: %s, op: %s' % (ks, op), html=True)
        errorInfo = ''
        for k in ks.split('_'):
            if not k:
                continue
            k = k.replace('*', '_')
            try:
                r = r[int(k)] if type(r) in (list, tuple) else r.get(k)
            except:
                r = None
            if r is None:
                errorInfo = '字段[%s] is not found' % k
                
        return r, '_' + op,k,errorInfo
    
    def _equal(self, r, v):
        
        assert r == v, '%s!=%s[actual:%s expect:%s]' %(r, v,r, v)
        
    
        
#     def _equal(self, r, v):
#         assert r == v, '$s %s != %s' %(r, v)
        
    def _eq(self, r, v):
        self._equal(r, v)
        
    def _iequal(self, r, v):
        assert str(r).lower() == str(v).lower(), '%s!=%s[actual:%s expect:%s}' %(r, v,r, v)
        
    def _inequal(self, r, v):
        assert str(r).lower() != str(v).lower(), '%s should not be equal with %s' %(r, v)
        
    def _ieq(self, r, v):
        self._iequal(r, v)

    def _ineq(self, r, v):
        self._inequal(r, v)
        
    def _nequal(self, r, v):
        assert r != v, '%s==%s , %s should not be equal with %s' %(r, v,r, v)
        
    def _neq(self, r, v):
        self._nequal(r, v)
        
    def _ne(self, r, v):
        self._nequal(r, v)
        
    def _contain(self, r, v):
        assert v in r, 'expression[%s] %s not contain %s' %(r, v)
        
    def _icontain(self, r, v):
        assert v.lower() in r.lower(), '%s not icontain %s' %(r, v)
        
    def _ncontain(self, r, v):
        assert v not in r, '%s contain %s' %(r, v)
        
    def _list_contain(self, r, v):
        try:
            v = json.loads(v)
        except:
            pass
        if type(v) != list:
            v = [v]
        for i in v:
            assert i in r, '%s not in %s' % (i, r)
    
    def _withinList(self, r, v):
        try:
            v = json.loads(v)
        except:
            pass
        if type(v) != list:
            v = [v]
        assert r in v, '%s not in %s' % (r, v)
        
    def _startswith(self, r, v):
        assert r.startswith(v), '%s not starts with %s' %(r, v)
        
    def _endswith(self, r, v):
        assert r.endswith(v), '%s not ends with %s' %(r, v)
        
    def _lt(self, r, v):
        assert float(r) < float(v), '%s >= %s' %(r, v)
        
    def _lte(self, r, v):
        assert float(r) <= float(v), '%s > %s' %(r, v)
        
    def _gt(self, r, v):
        assert float(r) > float(v), '%s <= %s' %(r, v)
        
    def _gte(self, r, v):
        assert float(r) >= float(v), '%s < %s' %(r, v)
        
    def _len(self, r, v):
        assert len(r) == int(v), 'len %s != %s' %(len(r), v)
        
    def _len_lt(self, r, v):
        assert len(r) < int(v), 'len %s >= %s' % (len(r), v)
        
    def _len_lte(self, r, v):
        assert len(r) <= int(v), 'len %s > %s' %(len(r), v)
        
    def _len_gt(self, r, v):
        assert len(r) > int(v), 'len %s <= %s' %(len(r), v)
        
    def _len_gte(self, r, v):
        assert len(r) >= int(v), 'len %s < %s' %(len(r), v)
        
    def __include(self, r, v):
        r_list = r if type(r) == list else [r]
        try:
            v_dict = json.loads(v)
            assert type(v_dict) == dict, 'only support json with dict format'
            for r in r_list:
                if isinstance(r, dict):
                    _equal = True
                    for k, v in v_dict.iteritems():
                        if v != r.get(k):
                            _equal = False
                            break
                    if _equal:
                        return True
            return False
        except:
            return v in r_list
    
    def _expect(self, r, v):
        try:
            v = json.loads(v)
        except:
            pass
        self._equal(r, v)
        
    def _include(self, r, v):
        assert self.__include(r, v), '%s not include %s' % (r, v)
    
    def _exclude(self, r, v):
        assert not self.__include(r, v), '%s include %s' % (r, v)
        
    def _regex(self, r, v):
        assert re.compile(v).match(r), '%s not match %s' % (r, v)
        
    def _isDigit(self, r,v):
        actual = re.compile('^[0-9]+$').match(str(r)) is not None
        assert actual == v, '%s != %s[actual:%s expect:%s}' % (str(actual),v,str(actual),v)
    
    def _isAlphabet(self,r,v):
        actual = re.compile('^[A-Za-z]+$').match(str(r)) is not None
        assert actual == v, '%s != %s[actual:%s expect:%s}' % (str(actual),v,str(actual),v)
    
    def _isAlphabetAndDigit(self,r,v):
        actual = re.compile('^[A-Za-z0-9]+$').match(str(r)) is not None
        assert actual == v, '%s != %s[actual:%s expect:%s}' % (str(actual),v,str(actual),v)
    
    def _isNotEmpty(self,r,v):
        actual1 = (str(r).strip()) != ''
        actual2 = (str(r).strip()) != 'null'
        actual3 = r is not None
        actual = actual1 and actual2 and actual3
        assert actual == v, '%s != %s[actual:%s expect:%s}' % (str(actual),v,str(actual),v)
      
    def _enum(self, r, v):
        assert r in json.loads(v), '%s not in %s' % (r, v)
        
    def _keys(self, r, v):
        print v
        if type(v) == list:
            pass
        else:
            v = json.loads(v) 
        rs = r if type(r) == list else [r]
        for r in rs:
            miss = set(v) - set(r.keys())
            extra = set(r.keys()) - set(v)
            assert len(extra) == 0 and len(miss) == 0, '实际的字段列表：%s, 多余的字段列表：%s, 缺少的字段列表：%s' % (r.keys(), list(extra), list(miss))
            
    def _listeq(self, r, v):
        if type(v) == list:
            pass
        else:
            v = [v]
        rs = r if type(r) == list else [r]
        miss = set(v) - set(rs)
        extra = set(rs) - set(v)
        assert len(extra) == 0 and len(miss) == 0, '实际的字段列表：%s, 多余的字段列表：%s, 缺少的字段列表：%s' % (rs, list(extra), list(miss))
            
    def _has_keys(self, r, v):
        self._keys(r, v)
    
    def _has_not_keys(self, r, v):
        if type(v) == list:
            pass
        else:
            v = json.loads(v) 
        rs = r if type(r) == list else [r]
        for r in rs:
            miss = set(v) - set(r.keys())
            extra = set(r.keys()) - set(v)
            assert len(extra) == len(r) and len(miss) == len(v), '实际的字段列表：%s, 多余的字段列表：%s, 缺少的字段列表：%s' % (r.keys(), list(extra), list(miss))
        
    def _include_keys(self, r, v):
        v = json.loads(v)
        rs = r if type(r) == list else [r]
        for r in rs:
            extra = set(v) - set(r.keys())
            assert len(extra) == 0, '%s has extra keys %s' % (r.keys(), extra)
        
    def _img_size(self, r, v):
        imgf = os.path.join(tempfile.mkdtemp(), os.path.basename(r))
        urlretrieve(r, imgf)
        with Image.open(imgf) as img:
            width_height = '%s:%s' % (img.width, img.height)
            assert width_height == v, '%s != %s' % (width_height, v)
    
    
    
        
    def filter_param_dict(self, kwargs):
        '''
        功能：
        - 将动态参数过滤分组成业务参数biz和校验参数verify
        
        参数：
        - kwargs 动态参数
        
        返回值：
        - biz, verify
            
        例子：
        - biz, verify = filter_param(**kwargs)
        '''
        biz, verify = {}, {}
        for key, value in kwargs.iteritems():
            if key.startswith('_'):
                verify[key] = value
            else:
                biz[key] = value
        logger.trace('biz: %s' % biz, True)
        logger.trace('verify: %s' % verify, True)
        return biz, verify
        
    def filter_param(self, **kwargs):
        '''
        功能：
        - 将动态参数过滤分组成业务参数biz和校验参数verify
        
        参数：
        - kwargs 动态参数
        
        返回值：
        - biz, verify
            
        例子：
        - biz, verify = filter_param(**kwargs)
        '''
        biz, verify = {}, {}
        for key, value in kwargs.iteritems():
            if key.startswith('_'):
                verify[key] = value
            else:
                biz[key] = value
        logger.trace('biz: %s' % biz, True)
        logger.trace('verify: %s' % verify, True)
        return biz, verify
        
    def validate(self, result, **kwargs):
        '''
        功能：
        - 用户对json格式详细校验
        
        参数：
        - result 服务端返回结果
        - kwargs 校验参数以下划线__前面部分为校验路径，路径用_分隔，后面部分为校验类型
        
        返回值：
        - 
            
        例子：
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | __include={"a": 1} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | __exclude={"a": 2} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _a=${1} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _a__equal=${1} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _b__regex=^a.c\d$ |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _c__len=${2} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _c__len_gt=${0} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _c_2_len=${0} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _c_2_expect={} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _d_a=${1} |
        | validate | {'a': 1, 'b': 'abc1', 'c': [1, 2, {}], 'd': {'a': 1, 'b': 2}} | _d_a=${1} | __include={"a": 1} |
        '''
        if not kwargs:
            return
        try:
            result = json.loads(result)
        except:
            pass
        
        testResultDetail = ''

        passResultList = []
        failResultList = []
        
        for key, v in kwargs.iteritems():

            try:
                r, op,k,errorInfo = self.__get_result_and_operate(result, key)
                getattr(self, op)(r, v)
                
                passResultList.append(k + ':pass (validatorExpression:' + key + ')')
                
            except AssertionError, e:
                failInfo = ''
                if errorInfo:
                    failInfo = k + ':fail (validatorExpression:' + key + ' and errorInfo:' + errorInfo + ')'
                else:
                    failInfo = k + ':fail (validatorExpression:' + key + ' and errorInfo:' + e.message + ')'
                failResultList.append(failInfo)
        
        noFail = False  
        
        resultList = failResultList + passResultList
        
        if len(resultList) == 1:
            testResultDetail = resultList[0]
        else:
            for result in resultList:
                testResultDetail = testResultDetail + result + '\n'
                
            testResultDetail = testResultDetail.rstrip('\n')     

        if len(failResultList) > 0:
            assert noFail, testResultDetail
        else:
            try:             
                b.set_test_message(testResultDetail)
            except RobotNotRunningError as e:
                print e
        print testResultDetail
        
       
         
validator = Validator()

if __name__ == '__main__':
    def setCommonParamsValidatorDict(**kwargs):
        return kwargs
    paramDict = setCommonParamsValidatorDict(_a=1, __exclude='{"a": 2}')
    def v (s, paramDict,**kwargs):
        kwargs=dict(paramDict, **kwargs)
        print kwargs
        validator.validate(s,**kwargs)
    v('{"a": 1, "b": "abc1", "c": [1, 2, 3], "d": 3}',paramDict,_d=3,_b='abc1',_a=1)
#                         'f': 'http://www.baidu.com/img/bd_logo1.png'},
#                __include='{"a": 1}', __exclude='{"a": 2}',
#                _a=1, _b='abc1', _c=[1, 2, 3], _e_0_a=1, _e_0_b__len=2,
#                _b__contain='c', _b__icontain='A',
#                _c__len=3, _c__len_gte=3, _c__len_gt=2, _c__len_lte=3, _c__len_lt=4,
#                _d__include='{"a": 1}', _d__exclude='{"a": 2}',
#                _e__include='{"a": 1}', _e__exclude='{"a": 3}',
#                _b__regex='^a.c\d$',
#                _f__img_size='540:258',
#                _c__list_contain='[1, 2]',
#                __has_keys='[]')
    
    