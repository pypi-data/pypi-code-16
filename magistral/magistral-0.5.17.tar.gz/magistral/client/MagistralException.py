'''
Created on 10 Aug 2016
@author: rizarse
'''

class MagistralException(Exception):
       
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)