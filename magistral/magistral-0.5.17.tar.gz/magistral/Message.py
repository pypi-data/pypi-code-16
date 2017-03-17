'''
Created on 13 Aug 2016
@author: rizarse
'''

class Message(object):

    def __init__(self, topic, channel, payload, index = 0, timestamp = 0):
        
        assert topic is not None, 'Topic is required'
        assert channel is not None, 'Channel is required' 
        assert payload is not None, 'Topic is required'
        
        assert isinstance(topic, str),' Topic must be type of str'
        assert isinstance(channel, int),' Topic must be type of int'
        assert isinstance(payload, bytes),' Topic must be type of bytes'
        
        self.__topic = topic;
        self.__channel = channel;
        self.__body = payload;
        self.__index = index;
        self.__timestamp = timestamp;
    
    def topic(self):
        return self.__topic;
    
    def channel(self):
        return self.__channel;
    
    def payload(self):
        return self.__body;
    
    def index(self):
        return self.__index;
    
    def timestamp(self):
        return self.__timestamp;