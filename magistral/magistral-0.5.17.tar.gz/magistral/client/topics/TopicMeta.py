'''
Created on 12 Aug 2016
@author: rizarse
'''

class TopicMeta(object):

    def __init__(self, topic, channels):        
        assert topic is not None, 'Topic name required'
        assert isinstance(topic, str), 'Topic name must be type of str'
        
        self.__topicName = topic
        self.__channels = channels

    def topic(self):
        return self.__topicName
    
    def channels(self):
        return self.__channels