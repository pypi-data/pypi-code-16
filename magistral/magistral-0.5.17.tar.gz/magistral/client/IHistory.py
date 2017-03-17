'''
Created on 13 Aug 2016
@author: rizarse
'''

from abc import abstractmethod
import time

class IHistory(object):
    
    @abstractmethod
    def history(self, topic, channel, count, start = 0, callback = None): pass

    @abstractmethod
    def historyIn(self, topic, channel, start = 0, end = int(round(time.time() * 1000)), callback = None): pass