'''
Created on 9 Aug 2016

@author: rizarse
'''

from abc import abstractmethod

class IMagistral :
    
    @abstractmethod
    def subscribe(self, topic, group = "default", channel = -1, listener = None, callback = None): pass
    
    @abstractmethod
    def unsubscribe(self, topic, channel = -1, callback = None): pass
    
    @abstractmethod
    def publish(self, topic, msg, channel = -1, callback = None): pass
    
    @abstractmethod
    def topics(self, callback = None): pass
    
    @abstractmethod
    def topic(self, topic, callback = None): pass
    
    @abstractmethod
    def close(self): pass
        