#encoding=utf8
'''
Created on 2015.7.17

@author: juncheng.cjc
'''
class Variable(object):
    '''
    author�?成文
    
    功能描述 测试数据用于不同环境
    
    依赖库：�?
    '''
    
    def daily(self):
        '''
        功能�?
        - 指定日常环境变量
        '''
        pass
    
    def online(self):
        '''
        功能�?
        - 指定线上环境变量
        '''
        pass
    
    def common(self):
        '''
        功能�?
        - 指定通用环境变量
        '''
        pass
    
    def get_variables(self, env='daily'):
        '''
        功能�?
        - 用于robot动�?获取变量
        '''
        self.common()
        if env.lower() in ('online', 'prepare'):
            self.online()
        else:
            self.daily()
        return self.__dict__