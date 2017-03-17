'''
Created on 9 Aug 2016
@author: rizarse
'''

from abc import abstractmethod


class IAccessControl :
    
    @abstractmethod
    def permissions(self, topic = None, callback = None): pass
    
    @abstractmethod
    def grant(self, user, topic, read, write, ttl = 0, channel = -1, callback = None): pass
    
    @abstractmethod
    def revoke(self, user, topic, channel = -1, callback = None): pass